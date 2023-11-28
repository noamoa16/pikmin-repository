const IMAGE_SIZE = 48;
const WIDTH = 5;
const HEIGHT = 6;
const PARTS_NAMES = [
    "Main_Engine",
    "Positron_Generator",
    "Eternal_Fuel_Dynamo",
    "Extraordinary_Bolt",
    "Whimsical_Radar",
    "Geiger_Counter",
    "Radiation_Canopy",
    "Sagittarius",
    "Shock_Absorber",
    "Automatic_Gear",
    "Number_1_Ionium_Jet",
    "Anti-Dioxin_Filter",
    "Omega_Stabilizer",
    "Gravity_Jumper",
    "Analog_Computer",
    "Guard_Satellite",
    "Libra",
    "Repair-type_Bolt",
    "Gluon_Drive",
    "Zirconium_Rotor",
    "Interstellar_Radio",
    "Pilot's_Seat",
    "Number_2_Ionium_Jet",
    "Bowsprit",
    "Chronos_Reactor",
    "Nova_Blaster",
    "Space_Float",
    "Massage_Machine",
    "UV_Lamp",
    "Secret_Safe"
];

const stopwatch = new Stopwatch();
let gameStarted = false;
let gameEnded = false;
let image = {};
let cell;

/**
 * @param {boolean} value
 * @return {void}
 */
function setArrowDisabled(value){
    for(let d of ["up", "left", "right", "down"]){
        $('#arrow-' + d).prop("disabled", value);
    }
}

// 矢印キーが使用可能かどうかチェックし、セットする
function checkArrowEnable(){
    let p = cell.indexOf(0);
    $('#arrow-up').prop("disabled", !isInner(p.x, p.y - 1));
    $('#arrow-left').prop("disabled", !isInner(p.x - 1, p.y));
    $('#arrow-right').prop("disabled", !isInner(p.x + 1, p.y));
    $('#arrow-down').prop("disabled", !isInner(p.x, p.y + 1));
}

function cellInit(){
    cell = Matrix.makeFilled(WIDTH, HEIGHT, "");
    for(let y = 0; y < HEIGHT; y++){
        for(let x = 0; x < WIDTH; x++){
            cell.set(x, y, x + y * WIDTH);
        }
    }
}

function isInner(x, y){
    return 0 <= x && x < WIDTH && 0 <= y && y < HEIGHT;
}

function swapCell(x1, y1, x2, y2){
    let tmp = cell.get(x1, y1);
    cell.set(x1, y1, cell.get(x2, y2));
    cell.set(x2, y2, tmp);
}

function moveUp(){
    if(!gameStarted) return;
    let p = cell.indexOf(0);
    if(isInner(p.x, p.y - 1)){
        swapCell(p.x, p.y, p.x, p.y - 1);
    }
    checkArrowEnable();
}
function moveLeft(){
    if(!gameStarted) return;
    let p = cell.indexOf(0);
    if(isInner(p.x - 1, p.y)){
        swapCell(p.x, p.y, p.x - 1, p.y);
    }
    checkArrowEnable();
}
function moveRight(){
    if(!gameStarted) return;
    let p = cell.indexOf(0);
    if(isInner(p.x + 1, p.y)){
        swapCell(p.x, p.y, p.x + 1, p.y);
    }
    checkArrowEnable();
}
function moveDown(){
    if(!gameStarted) return;
    let p = cell.indexOf(0);
    if(isInner(p.x, p.y + 1)){
        swapCell(p.x, p.y, p.x, p.y + 1);
    }
    checkArrowEnable();
}

function getTime(){
    let tdec = "--", tsec = "--", tmin = "--";
    if(gameStarted || gameEnded){
        let t = stopwatch.time;
        t = Math.min(t, 99 * 60 + 59 + 0.999)
        tdec = ("0" + (Math.floor(100 * t) % 100)).slice(-2);
        tsec = ("0" + (Math.floor(t) % 60)).slice(-2);
        tmin = ("0" + (Math.floor(t / 60))).slice(-2);
    }
    return {"min": tmin, "sec": tsec, "dec": tdec};
}

/**
 * @param {HTMLElement} canvas
 * @param {string} imageDirPath
 */
function start(canvas, imageDirPath){
    const fps = 30;
    setInterval(() => update(canvas), 1000 / fps);

    for(let i in PARTS_NAMES){
        image[i] = new Image();
        image[i].src = imageDirPath + "/" + PARTS_NAMES[i] + ".jpg";
    }

    cellInit();

    $('#reset').prop("disabled", true);
    $('#save').prop("disabled", true);
    setArrowDisabled(true);

	$('#start').on('click', function (e) {
        $('#start').prop("disabled", true);
        // シャッフル
        let numList = [...Array(WIDTH * HEIGHT).keys()];
        for(let i = 0; i < WIDTH * HEIGHT; i++){
            while(true){
                let index = Math.floor(Math.random() * (WIDTH * HEIGHT - i));
                if(numList[index] != i){
                    cell.set(i % WIDTH, Math.floor(i / WIDTH), numList[index]);
                    numList.splice(index, 1);
                    break;
                }
            }
        }
        stopwatch.start();
        gameStarted = true;
        $('#reset').prop("disabled", false);
        setArrowDisabled(false);
        checkArrowEnable();
    })
    
    $('#reset').on('click', function (e) {
        $('#reset').prop("disabled", true);
        $('#save').prop("disabled", true);
        gameStarted = false;
        gameEnded = false;
        cellInit();
        $('#start').prop("disabled", false);
        setArrowDisabled(true);
    })

    $('#arrow-up').on('click', function (e) {
        moveUp();
    })
    $('#arrow-left').on('click', function (e) {
        moveLeft();
    })
    $('#arrow-right').on('click', function (e) {
        moveRight();
    })
    $('#arrow-down').on('click', function (e) {
        moveDown();
    })

    $(window).keypress(function (e) {
        const func = {
            'w': moveUp,
            'W': moveUp,
            'a': moveLeft,
            'A': moveLeft,
            'd': moveRight,
            'D': moveRight,
            's': moveDown,
            'S': moveDown,
        }[e.key];
        if(func != undefined){
            func();
        }
	});

    $('#save').on('click', function (e) {
        let a = document.createElement('a');
        a.href = canvas.toDataURL();
        a.download = "30parts-puzzle-";
        let time = getTime();
        a.download += time.min + time.sec + time.dec;
        a.download += ".png"
        a.click();
    })
}

/**
 * @param {HTMLElement} canvas
 */
function update(canvas){
    /** @type {CanvasRenderingContext2D} */
    const context = canvas.getContext("2d");

    // ゲームクリア
    if(gameStarted){
        let ok = true;
        for(let y = 0; y < HEIGHT; y++){
            for(let x = 0; x < WIDTH; x++){
                let correct = x + y * WIDTH;
                let current = cell.get(x, y);
                if(correct != current){
                    ok = false;
                    break;
                }
            }
            if(!ok) break;
        }

        if(ok){
            gameStarted = false;
            gameEnded = true;
            stopwatch.stop();
            $('#save').prop("disabled", false);
            setArrowDisabled(true);
        }
    }

    context.clearRect(0, 0, canvas.width, canvas.height);

    for(let y = 0; y < HEIGHT; y++){
        for(let x = 0; x < WIDTH; x++){
            if(cell.get(x, y) !== ""){
                context.drawImage(
                    image[cell.get(x, y)], x * IMAGE_SIZE, y * IMAGE_SIZE, 
                    IMAGE_SIZE, IMAGE_SIZE
                );
                context.font = "24px Arial";
                context.fillStyle = 'black';
                context.fillText(
                    cell.get(x, y) + 1,
                    cell.get(x, y) + 1 < 10 ? (x + 3 / 8) * IMAGE_SIZE : (x + 1 / 4) * IMAGE_SIZE,
                    (y + 5 / 8) * IMAGE_SIZE
                );
            }
        }
    }

    context.font = "16px Arial";
    context.fillStyle = 'black';
    let time = getTime();
    context.fillText("Time: " + time.min + ":" + time.sec + "." + time.dec,
        IMAGE_SIZE * WIDTH + 16, 30);
    
    let p = cell.indexOf(0);
    context.lineWidth = 3;
    context.strokeStyle = "red";
    context.beginPath();
    context.moveTo(p.x * IMAGE_SIZE, p.y * IMAGE_SIZE);
    context.lineTo((p.x + 1) * IMAGE_SIZE, p.y * IMAGE_SIZE);
    context.lineTo((p.x + 1) * IMAGE_SIZE, (p.y + 1) * IMAGE_SIZE);
    context.lineTo(p.x * IMAGE_SIZE, (p.y + 1) * IMAGE_SIZE);
    context.closePath();
    context.stroke();
}