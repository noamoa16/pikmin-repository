const OBJECT_NAMES = ["egg", "nectar", "wnectar", "spicy", "bitter", "mitites"];
const IMAGE_SIZE = 48;
const WIDTH = 10;
const HEIGHT = 10;
let image = {};
let breakingStarted = false;
let broken;

let board = undefined;
function initBoard(){
    board = Matrix.makeFilled(WIDTH, HEIGHT, "egg");
}
initBoard();

function spawnFromEgg(){
    let r = Math.random();
    if(r < 0.5) return "nectar";
    else if(r < 0.85) return "wnectar";
    else if(r < 0.9) return "spicy";
    else if(r < 0.95) return "bitter";
    else return "mitites";
}

/**
 * @param {HTMLElement} canvas
 * @param {string} imageDirPath
 */
function start(canvas, imageDirPath){
    const fps = 30;
    setInterval(() => update(canvas), 1000 / fps);

    for(let objectName of OBJECT_NAMES){
        image[objectName] = new Image();
        image[objectName].src = imageDirPath + "/" + objectName + ".png";
    }

	$('#break').on('click', function (e) {
        breakingStarted = true;
        broken = 0;
        $('#break').prop("disabled", true); // breakを無効に
    })

    $('#reset').on('click', function (e) {
        breakingStarted = false;
        board = Matrix.makeFilled(WIDTH, HEIGHT, "egg");
        $('#break').prop("disabled", false); // breakを有効に
    })

    $('#save').on('click', function (e) {
        let filename = "egg-lottery-" 
            + OBJECT_NAMES
            .filter(name => name != "egg")
            .map(name => board.count(name))
            .join("-") + ".png";

        let a = document.createElement('a');
        a.href = canvas.toDataURL(/*'image/png', 0.85*/);
        a.download = filename;
        a.click();
    })
}

/**
 * @param {HTMLElement} canvas
 */
 function update(canvas){
    /** @type {CanvasRenderingContext2D} */
    const context = canvas.getContext("2d");
    context.clearRect(0, 0, canvas.width, canvas.height);

    if(breakingStarted){
        if(broken < WIDTH * HEIGHT){
            let x = broken % WIDTH;
            let y = Math.floor(broken / WIDTH);
            board.set(x, y, spawnFromEgg());
            broken++;
        }
    }
    
    for(let y = 0; y < HEIGHT; y++){
        for(let x = 0; x < WIDTH; x++){
            context.drawImage(
                image[board.get(x, y)], x * IMAGE_SIZE, y * IMAGE_SIZE, 
                IMAGE_SIZE, IMAGE_SIZE
            );
        }
    }

    context.font = "16px Arial";
    context.fillStyle = 'black';
    context.fillText(
        "エキス : " + board.count("nectar"), 480, 30);
    context.fillText(
        "2エキス : " + board.count("wnectar"), 480, 60);
    context.fillText(
        "ゲキカラ : " + board.count("spicy"), 480, 90);
    context.fillText(
        "ゲキニガ : " + board.count("bitter"), 480, 120);
    context.fillText(
        "タマゴムシ : " + board.count("mitites"), 480, 150);
}