let audioElement;
let analyser;
let firstPlay = true;
const FREQUENCY_BIN_COUNT = 128;
const dataArray = new Uint8Array(FREQUENCY_BIN_COUNT);

const setupAudioCtx = () => {
    // Create audio context
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
    // Initialize analyser
    analyser = audioCtx.createAnalyser();
    analyser.fftSize = 2 * FREQUENCY_BIN_COUNT;
    // Analyser's frequencyBinCount is always half of the fftSize (https://developer.mozilla.org/en-US/docs/Web/API/AnalyserNode/frequencyBinCount)
    const source = audioCtx.createMediaElementSource(audioElement);
    // Connect source -> analyser -> destination
    source.connect(analyser);
    analyser.connect(audioCtx.destination);
}

const draw = () => {
    analyser.getByteFrequencyData(dataArray);
    for (let i = 0; i < FREQUENCY_BIN_COUNT; i++) {
        const binI = document.getElementById(`bin-${i}`);
        binI.innerHTML = dataArray[i] === 0 ? '_' : '█'.repeat(dataArray[i]);
    }
};

const setupOnPlay = () => {
    if (firstPlay) {
        setupAudioCtx();
        setInterval(draw, 50);
        firstPlay = false;
    }
};

// When the page loads, create a div for each bin, to be filled up with text
window.onload = () => {
    const createBins = () => {
        for (let i = 0; i < FREQUENCY_BIN_COUNT; i++) {
            const bin = document.createElement("div");
            bin.setAttribute("id", `bin-${i}`);
            bin.innerHTML = '_';
            document.getElementById("spectrogram").appendChild(bin);
        }
    };

    const getAudioElement = () => {
        audioElement = document.querySelector('audio');
        audioElement.onplay = setupOnPlay;
    };

    createBins();
    getAudioElement();
};
