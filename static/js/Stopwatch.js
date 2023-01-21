class Stopwatch{
    _start = undefined;
    _stop = undefined;
    _started = false;

    /**
     * @returns {void}
     */
    start(){
        this._start = new Date().getTime();
        this._started = true;
    }
    /**
     * @returns {void}
     */
    stop(){
        this._stop = new Date().getTime();
        this._started = false;
    }
    /**
     * @returns {number}
     */
    get time(){
        return this._started ?
            (new Date().getTime() - this._start) / 1000:
            (this._stop - this._start) / 1000;
    }
    /**
     * @returns {boolean}
     */
    get started(){
        return this._started;
    }
}