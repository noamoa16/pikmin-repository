class Matrix{
    constructor(array2d = []) {
        this.width = 0;
        for (let row of array2d) {
            this.width = Math.max(row.length, this.width);
        }
        this.height = array2d.length;
        this.cell = [];
        for (let y = 0; y < this.height; y++){
            this.cell[y] = new Array(this.width);
            for (let x = 0; x < this.width; x++) {
                this.cell[y][x] = array2d[y][x];
            }
        }
    }

    /**
     * @param {number} width 
     * @param {number} height 
     * @param {any} fill 
     * @returns {Matrix}
     */
    static makeFilled(width, height, fill = undefined) { // -> Matrix
        let isFunc = (typeof fill) == "function"; // bool
        let array2d = [];
        for (let y = 0; y < height; y++){
            array2d[y] = new Array(width);
            for (let x = 0; x < width; x++) {
                array2d[y][x] = isFunc ? fill(x, y) : fill;
            }
        }
        return new Matrix(array2d);
    }

    /**
     * @param {any} arg 
     * @returns {number}
     */
    count(arg) {
        let isFunc = (typeof arg) == "function"; // bool
        let ret = 0;
        for(let y = 0; y < this.height; y++){
            for (let x = 0; x < this.width; x++){
                if (isFunc) {
                    if (arg(this.cell[y][x])) {
                        ret++;
                    }
                }
                else {
                    if (this.cell[y][x] == arg) {
                        ret++;
                    }
                }
            }
        }
        return ret;
    }

    /**
     * @returns {string}
     */
    toString() {
        let ret = "[\n";
        for (let y = 0; y < this.height; y++) {
            ret += "  [";
            for(let x = 0; x < this.width; x++){
                if (typeof this.cell[y][x] == "string") {
                    ret += "'" + this.cell[y][x] + "'";
                }
                else {
                    ret += this.cell[y][x];
                }
                if (x != this.width - 1) ret += ", ";
            }
            ret += "]";
            if (y != this.height - 1) ret += ",";
            ret += "\n";
        }
        ret += "]";
        return ret;
    }

    /**
     * @param {number} x 
     * @param {number} y 
     * @returns {any}
     */
    get(x, y) {
        return this.cell[y][x];
    }
    /**
     * @param {number} x 
     * @param {number} y 
     * @param {any} value
     */
    set(x, y, value) {
        this.cell[y][x] = value;
    }

    /**
     * @param {*} value 
     * @returns 
     */
    indexOf(value) {
        for (let y = 0; y < this.height; y++){
            for (let x = 0; x < this.width; x++) {
                if (this.get(x, y) == value) {
                    return { 'x': x, 'y': y };
                }
            }
        }
        return undefined;
    }
}