const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);

const bookTitle = decodeURIComponent(urlParams.get('title'));
document.getElementById('BookTitle').innerHTML = bookTitle;



let currentImageIndex = 1;
let currentSentence = 0;
var totalPages;
var genData;
var curUser = document.getElementById('Profile').textContent;
var sections = [];
var gptData = {};
var isDataGen = false;
var isKeyWord = false;
var isReview = false;
var synthesis = window.speechSynthesis;
let sessionStartTime;
let sessionDuration = 0;
let year;
let month;
let day;
let isDataLoaded = false; 
let isAudioEnded = false; 
let readMode = 0;


const toggle = document.getElementById('toggle');
const modeText = document.getElementById('modeText');

toggle.addEventListener('change', function() {
    localStorage.setItem('currentPage', currentImageIndex.toString());
    if (toggle.checked) {
    modeText.textContent = '科学知识学习';
    readMode = 1;
    window.location.href= './bookDetail?title=' + encodeURIComponent(bookTitle); 
  } else {
    modeText.textContent = '绘本阅读';
    readMode = 0;
    window.location.href= './bookRead?title=' + encodeURIComponent(bookTitle); 
  }
});

currentImageIndex = parseInt(localStorage.getItem('currentPage'), 10) || 1;

function toggleMenu() {
    const fab = document.querySelector('.fab');
    const fabMenu = document.getElementById('fab-menu');
  
    if (fabMenu.style.display === 'none' || fabMenu.style.display === '') {
      fabMenu.style.display = 'flex';
      setTimeout(() => {
        fabMenu.style.transform = 'scale(1)';
      }, 0);
      fab.style.transform = 'rotate(45deg)';
    } else {
      fabMenu.style.transform = 'scale(0)';
      setTimeout(() => {
        fabMenu.style.display = 'none';
      }, 300);
      fab.style.transform = 'rotate(0deg)';
    }
  }
  
function startSessionTimer() {
    sessionStartTime = new Date().getTime(); // Get current time
}

function updateSessionDuration() {
    const currentTime = new Date().getTime();
    sessionDuration = Math.floor( (currentTime - sessionStartTime) / 60000); // count time interval (minute)
}

window.onload = function() {
    startSessionTimer();
};

function switchPage(add){
    updateSessionDuration();
    fetch('/api/timer', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            duration: sessionDuration,
            year: new Date().getTime().getFullYear,
            month: new Date().getTime().getMonth + 1,
            day: new Date().getTime().getDate,
            title: bookTitle,
            username: curUser
        }),
    })
    .then(response => response.json())
    .then(data => {
    })
    .catch((error) => {
        console.error('Error update duration:', error);
    });
    console.log("User session duration:", sessionDuration, "minutes");
    window.location.href = add;
}

function getUser(){
    fetch('/api/user', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({}),
    })
    .then(response => response.json())
    .then(data => {
        curUser = data.username;
        document.getElementById('Profile').innerHTML = data.username;
        fetchBook();
    })
    .catch((error) => {
        console.error('Error get user information:', error);
    });
}

function fetchBook(){
    console.log({ 
        username: curUser,
        title: bookTitle 
    });
    fetch('/api/gen', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
            username: curUser,
            title: bookTitle 
        }),
    })
    .then(response => response.json())
    .then(data => {
        genData = data.generation;
        gptData = data.answerProgress;
        console.log(genData);
        console.log(gptData);
        totalPages = Object.keys(genData).length;
        currentImageIndex = parseInt(localStorage.getItem('currentPage'), 10) || 1;
        console.log(currentImageIndex)
        isDataGen = true;
        if (isDataGen){
            textAudio();
            showImage();
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function render_caption(textData){
    let paragraph = document.createElement("div");
    const caption = document.getElementById('Caption');
    paragraph.className = "paragraph";
    paragraph.innerHTML = "";
    if(typeof textData == 'string'){
        paragraph.innerHTML += textData;
    }
    else{
        textData.forEach(function (e) {
            paragraph.innerHTML += `<div id="s${e.id}" class="sentence">${e.word}</div>`
        })
    }
    if(caption.childNodes.length == 0){
        caption.appendChild(paragraph);
    }
    else{
        caption.replaceChild(paragraph, caption.childNodes[0]);
    }
}

function playAudio(audioSrc) {
    isAudioEnded = false;
    audioPlayer.src = audioSrc;
    audioPlayer.play();
    audioPlayer.addEventListener('ended', playNextSentence);
}


function playNextSentence() {
    if (currentSentence < sections[currentImageIndex-1].length -1) {
        currentSentence++;
        playAudio(sections[currentImageIndex-1][currentSentence].audio);
        render_caption(sections[currentImageIndex-1][currentSentence].text);
    }
    else{
        audioPlayer.removeEventListener('ended', playNextSentence);
    } 
}

function updateProgressBar() {
    const progressBar = document.querySelector('.progress');
    const progressPercentage = (currentImageIndex / (totalPages)) * 100;
    progressBar.style.width = `${progressPercentage}%`;
    document.getElementById('curPage').innerHTML = `第${currentImageIndex}/${totalPages}页`;
}

function showImage() {
    /* isKeyWord = false; */
    if (currentImageIndex == 1){
        document.getElementById('prevPageIcon').style.visibility = 'hidden';
    }
    else{
        document.getElementById('prevPageIcon').style.visibility = 'visible';
    }
    if (currentImageIndex == totalPages){
        document.getElementById('nextPageIcon').style.visibility = 'hidden';
    }
    else{
        document.getElementById('nextPageIcon').style.visibility = 'visible';
    }
    const currentImage = document.getElementById("BookImg");
    currentImage.src = `../static/files/books/${bookTitle}/pages/page${currentImageIndex}.jpg`;
    updateProgressBar();
    currentSentence = 0;

    const audioPlayer = document.getElementById('audioPlayer');
    audioPlayer.removeEventListener('ended', playNextSentence);
    audioPlayer.pause();
    audioPlayer.currentTime = 0;

    playAudio(sections[currentImageIndex-1][currentSentence].audio);
    render_caption(sections[currentImageIndex-1][currentSentence].text);
}

function NextPage() {
    currentImageIndex = currentImageIndex < totalPages ? currentImageIndex + 1 : currentImageIndex;
    showImage();
}

function PrevPage() {
    currentImageIndex = currentImageIndex > 1 ? currentImageIndex - 1 : currentImageIndex;
    showImage();
}

/* Empty page does not have an audio file */
function textAudio(){
    sections = [];
    let i = 0;
    for (let key in genData){
        var sentences = [];
        let j = 0;
        for (let sen in genData[key]['section']){
            sentences.push({
                "text": genData[key]['section'][sen],
                "audio": `../static/files/books/${bookTitle}/audio/p${i}sec${j}.mp3`
            })
            j += 1;
        }
        sections.push(sentences)
        i += 1;
    }
    console.log(sections);
}

fetchBook();