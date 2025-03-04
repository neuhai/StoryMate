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
var persona = {};
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
let isExpPlayed = false;
let isExpEnded = false;
let isSumPlayed = false;
let isConvPlayed = false;
let isKnowledge = false;
let readMode = 0;
var CogLevel = 2;
var sum_id = 2;

const toggle = document.getElementById('toggle');
toggle.checked = true;
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

currentImageIndex = parseInt(localStorage.getItem('currentPage'), 10) || 1;

document.getElementById('questionSlider').addEventListener('input', function() {
    const value = this.value;
    handleSliderChange(value);
});

function handleSliderChange(value) {
    switch(value) {
        case '1':
            CogLevel = 1;
            break;
        case '2':
            CogLevel = 2;
            break;
        case '3':
            CogLevel = 3;
            break;
        default:
            console.log('未知值');
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


function getPersona(){
    fetch('/api/persona', {
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
        persona = data;
        console.log(persona);
        if(persona.isFill == 0 && persona.isSkip == 0){
            window.location.href= './information?title=' + encodeURIComponent(bookTitle); 
        }
        else{

        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
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
        fetchGenData();
    })
    .catch((error) => {
        console.error('Error get user information:', error);
    });
}

function fetchGenData(){
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
    console.log(CogLevel);
    paragraph.className = "paragraph";
    paragraph.innerHTML = "";
    if(typeof textData === 'string'){
        paragraph.innerHTML += textData;
    }
    else{
        textData.forEach(function (e) {
            if (e.keyword == 0){
                paragraph.innerHTML += `<div id="s${e.id}" class="sentence">${e.word}</div>`
            }
            else if (gptData[(currentImageIndex-1).toString()].cog > CogLevel){
                paragraph.innerHTML += `<div id="s${e.id}" class="sentence">${e.word}</div>`
            }
            else {
                paragraph.innerHTML += `<div id="s${e.id}" class="sentence_key" >${e.word}</div>`
                isKeyWord = true;
            }
        })
        if (isKeyWord && gptData[(currentImageIndex-1).toString()].cog <= CogLevel){
            console.log(gptData[(currentImageIndex-1).toString()]);
            console.log(currentSentence, sections[currentImageIndex-1].length)
            if(!gptData[(currentImageIndex-1).toString()].answer){
                // genConv();
                if(!isKnowledge){
                    genKG();
                    isKnowledge = true;
                }
                if(currentSentence == sections[currentImageIndex-1].length - 1){
                    genConv();
                }
            }
            else{
                review();
            }
        }
    }
    if(caption.childNodes.length == 0){
        caption.appendChild(paragraph);
    }
    else{
        caption.replaceChild(paragraph, caption.childNodes[0]);
    }
}

function genKG(){
    const container = document.querySelector('.container');
    let knowledge = document.createElement("div");
    knowledge.className = 'Knowledge';
    knowledge.innerHTML = `<div class="keyWord">
                            <div id="bubble">
                                <p1 id="Word">${gptData[(currentImageIndex-1).toString()].keyword}</p1>
                                </br>
                                <p2 id="Exp">${gptData[(currentImageIndex-1).toString()].explanation}</p2>
                            </div>
                         </div>`;
    
    if(document.querySelector('.Knowledge') == null){
        container.appendChild(knowledge);
    }
    else{
        console.log(document.querySelector('.Knowledge').innerHTML)
    }
}

function genConv(){
    const container = document.querySelector('.container');
    const knowledge = document.querySelector('.Knowledge');

    isDataLoaded = false;
    isConvPlayed = false;

    fetch('/api/conv', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            username: curUser,
            id: (currentImageIndex-1).toString(),
            title: bookTitle
         })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);

        let chatBox = document.createElement("div");
        chatBox.className = 'chatBox';
        chatBox.innerHTML = `
                            <div class="chatHistory">
                            </div>
                            <div class="topContent">
                                <img id='penguin' src='../static/files/imgs/penguin.png' />
                                <div id='chatContent'>
                                </div>
                            </div>`
        knowledge.appendChild(chatBox);
        document.getElementById('chatContent').innerHTML = `<p1>${data.greeting} </p1></br><p3>${data.question}</p3>`;
        if(document.querySelector('.inputBlock')){
            return;
        }
        document.querySelector('.chatBox').innerHTML += `<div class='inputBlock'>
                                <div id="overlay"></div>
                                <textarea id="textInput"></textarea>
                                <div id="candidateAnswer">
                                    <button class="indicate" onclick="indicate_answer('我不太清楚')">
                                        我不太清楚
                                    </button>
                                    <button class="indicate" onclick="indicate_answer('我想知道更多')">
                                        我想知道更多
                                    </button>
                                    <button class="replayConv" onclick="replay_conv()">
                                        重播🔂
                                    </button>
                                </div>
                                <hr>
                                <button id="voiceInputBtn" onclick="toggleVoiceInput('conv')">
                                    <img src='../static/files/imgs/voiceInput.png'>点击按钮开始回答！
                                </button>
                                <img id='loading' src="../static/files/imgs/loading.gif">
                              </div>`
        /* knowledge.innerHTML += `<div class='submitBlock'>
                              <button id="submitBtn" onclick="submitText()">
                                <span>Send my answer!</span>
                              </button>
                          </div>`; */
        /*console.log(chatBox.innerHTML);*/
        /*document.getElementById('response').innerHTML = data.response;*/
        
        /*isDataLoaded = true;
        if (!isAudioEnded){
            const audioPlayer = document.getElementById('audioPlayer');
            audioPlayer.addEventListener('ended', function () {
                isAudioEnded = true;
                if (!isExpPlayed) { 
                    playExpAudio();
                    const ExpAudioPlayer = document.getElementById('expAudioPlayer');
                    ExpAudioPlayer.addEventListener('ended', function () {
                        isExpEnded = true;
                        isExpPlayed = true;
                        if (!isConvPlayed) {
                            playConvAudio();
                            isConvPlayed = true;
                        }
                        isConvPlayed = true;
                    });
                }
                audioPlayer.removeEventListener('ended', arguments.callee);
            });
        }
        if (!isExpPlayed){
            const ExpAudioPlayer = document.getElementById('expAudioPlayer');
            ExpAudioPlayer.addEventListener('ended', function () {
                isExpEnded = true;
                isExpPlayed = true;
                if (!isConvPlayed) {
                    playConvAudio();
                    isConvPlayed = true;
                }
            });
            playExpAudio();
        }*/
        console.log(isExpEnded, isExpPlayed, isConvPlayed);
        if(isExpEnded && !isConvPlayed){
            document.getElementById('convAudioPlayer').addEventListener('ended', function () {
                isConvPlayed = true;
            });
            playConvAudio();
        }
    })
    .catch(error => console.error('Error:', error));
}

function indicate_answer(ans){
    const textInput = document.getElementById('textInput');
    textInput.value = ans;
    const voiceInputBtn = document.getElementById('voiceInputBtn');
    /*voiceInputBtn.innerHTML = `<img src='../static/files/imgs/voiceInput.png'>点击按钮开始回答！`;*/
}

function replay_conv(){
    playConvAudio();
}

function playAudio(audioSrc) {
    isAudioEnded = false;
    audioPlayer.src = audioSrc;
    audioPlayer.play();
    audioPlayer.addEventListener('ended', playNextSentence);
}

function playConvAudio(){
    if (isKeyWord && !isReview){
        convAudioPlayer.src = `../static/files/${curUser}/${bookTitle}/conv_audio/sec_${(currentImageIndex-1)}_q_1.mp3`;
        convAudioPlayer.play();
    }
}

function playExpAudio(){
    if (isKeyWord && !isReview){
        isExpEnded = false;
        expAudioPlayer.src = `../static/files/books/${bookTitle}/exp_audio/exp_audio${(currentImageIndex-1)}.mp3`;
        expAudioPlayer.play();
    }
}

function playSumAudio(audioSrc){
    isSumEnded = false;
    sumAudioPlayer.src = audioSrc;
    sumAudioPlayer.play();
}

function playNextSentence() {
    if (currentSentence == sections[currentImageIndex-1].length - 1){
        /* playExpAudio(); */
        audioPlayer.removeEventListener('ended', playNextSentence);
        if(isKeyWord&&!isReview){
            if (!isExpPlayed){
                const ExpAudioPlayer = document.getElementById('expAudioPlayer');
                ExpAudioPlayer.addEventListener('ended', function () {
                    isExpEnded = true;
                    isExpPlayed = true;
                    if (!isConvPlayed) {
                        document.getElementById('convAudioPlayer').addEventListener('ended', function () {
                            isConvPlayed = true;
                        });
                        playConvAudio();
                    }
                });
                playExpAudio();
            }
        } 
    } 
    if (currentSentence < sections[currentImageIndex-1].length -1) {
        currentSentence++;
        playAudio(sections[currentImageIndex-1][currentSentence].audio);
        render_caption(sections[currentImageIndex-1][currentSentence].text);
    }
        /* add another factor: this is the first time to answer */
        /*if (isKeyWord && !isReview){
            /* If in Review mode, do not play */
            /*playConvAudio();*/
        /*}*/
}

function updateProgressBar() {
    const progressBar = document.querySelector('.progress');
    const progressPercentage = (currentImageIndex / (totalPages)) * 100;
    progressBar.style.width = `${progressPercentage}%`;
    document.getElementById('curPage').innerHTML = `第${currentImageIndex}/${totalPages}页`;
}

function showImage() {
    /* isKeyWord = false; */
    isExpPlayed = false;
    isConvPlayed = false;
    isExpEnded = false;
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
    isKnowledge = false;
    const currentImage = document.getElementById("BookImg");
    currentImage.src = `../static/files/books/${bookTitle}/pages/page${currentImageIndex}.jpg`;
    updateProgressBar();
    currentSentence = 0;

    const audioPlayer = document.getElementById('audioPlayer');
    audioPlayer.removeEventListener('ended', playNextSentence);
    audioPlayer.pause();
    audioPlayer.currentTime = 0;

    convAudioPlayer.pause();
    convAudioPlayer.currentTime = 0;

    playAudio(sections[currentImageIndex-1][currentSentence].audio);
    render_caption(sections[currentImageIndex-1][currentSentence].text);
}

function NextPage() {
    console.log(currentImageIndex);
    isKeyWord = false;
    isReview = false;
    if (document.querySelector('.Knowledge') != null){
        save_knowledge_state(true, 'false', () => {
            currentImageIndex = currentImageIndex < totalPages ? currentImageIndex + 1 : currentImageIndex;
            showImage();
        })
        /* save_knowledge_state(true, 'false'); */
    }
    else {
        currentImageIndex = currentImageIndex < totalPages ? currentImageIndex + 1 : currentImageIndex;
        showImage();
        if(currentImageIndex == totalPages){
            summary();
        }
    }
}

function summary(){
    if(document.querySelector('.container').querySelector('.Knowledge')){
        document.querySelector('.container').removeChild(document.querySelector('.Knowledge'));
    }
    fetch('/api/sum', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            username: curUser,
            title: bookTitle
         })
    })
    .then(response => response.json())
    .then(data => {
        console.log(data);
        const container = document.querySelector('.container');
        let knowledge = document.createElement("div");
        knowledge.className = 'Knowledge';
        if(document.querySelector('.Knowledge') == null){
            container.appendChild(knowledge);
        }
        let chatBox = document.createElement("div");
        chatBox.className = 'chatBox';
        chatBox.innerHTML = `
                            <div class="chatHistory">
                            </div>
                            <div class="topContent">
                                <img id='penguin' src='../static/files/imgs/penguin.png' />
                                <div id='chatContent'>
                                </div>
                            </div>`
        knowledge.appendChild(chatBox);
        document.getElementById('chatContent').innerHTML = `<p1>${data.greeting} </p1></br><p3>${data.question}</p3>`;
        if(document.querySelector('.inputBlock')){
            return;
        }
        document.querySelector('.chatBox').innerHTML += `<div class='inputBlock'>
                                <div id="overlay"></div>
                                <textarea id="textInput"></textarea>
                                <button id="voiceInputBtn" onclick="toggleVoiceInput('sum')">
                                    <img src='../static/files/imgs/voiceInput.png'>点击按钮开始回答！
                                </button>
                                <img id='loading' src="../static/files/imgs/loading.gif">
                              </div>`
        console.log(isSumPlayed);
        if(!isSumPlayed){
            document.getElementById('sumAudioPlayer').addEventListener('ended', function () {
                isSumPlayed = true;
            });
            playSumAudio(`../static/files/${curUser}/${bookTitle}/sum_audio/q_1.mp3`);
        }
    })
    .catch(error => console.error('Error:', error));
}

function PrevPage() {
    isReview = false;
    if (document.querySelector('.Knowledge') != null){
        save_knowledge_state(true, 'false', () => {
            currentImageIndex = currentImageIndex > 1 ? currentImageIndex - 1 : currentImageIndex;
            showImage();
        })
        /* save_knowledge_state(true, 'false'); */
    }
    else {
        currentImageIndex = currentImageIndex > 1 ? currentImageIndex - 1 : currentImageIndex;
        showImage();
    }
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

let recognition;
let recognizing = false;

function toggleVoiceInput(version) {
    const textInput = document.getElementById('textInput');
    const voiceInputBtn = document.getElementById('voiceInputBtn');

    if (recognizing) {
        // Stop recognition
        recognition.stop();
        recognizing = false;
        voiceInputBtn.innerHTML = `<img src='../static/files/imgs/voiceInput.png'>点击按钮开始回答！`;
        if(version == 'conv'){
            submitConv();
        }
        else if(version == 'sum'){
            submitSum();
        }
    } else {
        // Start recognition
        textInput.style.visibility = 'visible';
        voiceInputBtn.innerHTML = `<img src='../static/files/imgs/voiceInput.png'>说话中...点击按钮提交我的回答！`;

        if ('webkitSpeechRecognition' in window) {
            recognition = new webkitSpeechRecognition();
            recognition.lang = 'zh-CN';

            recognition.onresult = function(event) {
                const result = event.results[0][0].transcript;
                textInput.value = result;
                textInput.removeAttribute('readonly');
            };

            recognition.start();
            recognizing = true;
        } else {
            alert('Sorry, your browser does not support speech recognition!');
        }
    }
}

function startVoiceInput() {
    const textInput = document.getElementById('textInput');
    textInput.style.visibility = 'visible';
    const submitBtn = document.getElementById('submitBtn');
    submitBtn.style.visibility = 'visible';
    voiceInputBtn.innerHTML = `<img src='../static/files/imgs/voiceInput.png'>Speaking...`;
    if ('webkitSpeechRecognition' in window) {
      const recognition = new webkitSpeechRecognition();
      recognition.lang = 'en-US';

      recognition.onresult = function(event) {
        const result = event.results[0][0].transcript;
        textInput.value = result;
        textInput.removeAttribute('readonly');
        voiceInputBtn.innerHTML = `<img src='../static/files/imgs/voiceInput.png'>点击按钮开始回答！`;
      };

      recognition.start();
    } else {
      alert('Sorry, your browser does not support speech recognition!');
    }
}

function submitConv() {
    const textInput = document.getElementById('textInput');
    document.getElementById('loading').style.display = 'block';
    document.getElementById('overlay').style.display = 'block';
    /* if(textInput.value == ''){
        alert("You need to answer this question first!");
        return;
    } */
    console.log(textInput.value)
    fetch('/api/chat', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            username: curUser,
            id: (currentImageIndex-1).toString(),
            title: bookTitle,
            response: textInput.value,
         })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('overlay').style.display = 'none';
        gptData[(currentImageIndex-1).toString()].answer = true;
        console.log(data);
        response_dict = data.response_dict;
        curQA = data.QA_pair;
        const convAudioPlayer = document.getElementById('convAudioPlayer');
        convAudioPlayer.src = `../static/files/${curUser}/${bookTitle}/conv_audio/sec_${(currentImageIndex-1)}_q_${response_dict.q_id}.mp3`;
        convAudioPlayer.play();
        document.getElementById('textInput').value = '';
        /* addStar(data); */
        if(response_dict.end.toString().toLowerCase() == 'true'){
            document.getElementById('chatContent').innerHTML = `<p1>${response_dict.feedback} </p1><p2>${response_dict.explanation} </p2><p2>${response_dict.transition} </p2>`;
            document.querySelector('.inputBlock').remove();
            /* document.querySelector('.submitBlock').remove(); */
            document.querySelector('.Knowledge').innerHTML += `<div id='continueBlock'>
                                        <button id="continue" onclick="continueRead()">继续阅读！</button>
                                    </div>`;
        }
        else{
            document.getElementById('chatContent').innerHTML = `<p1>${response_dict.feedback} </p1><p2>${response_dict.explanation} </p2><p2>${response_dict.transition} </p2></br><p3>${response_dict.question} </p3>`;
        }
        updateChatHistory(response_dict, textInput.value);
        save_knowledge_state(false, response_dict.end);
    })
    .catch(error => console.error('Error:', error));
}

function submitSum() {
    const textInput = document.getElementById('textInput');
    document.getElementById('loading').style.display = 'block';
    document.getElementById('overlay').style.display = 'block';
    /* if(textInput.value == ''){
        alert("You need to answer this question first!");
        return;
    } */
    console.log(textInput.value)
    fetch('/api/answer_sum', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            username: curUser,
            title: bookTitle,
            id: sum_id,
            response: textInput.value,
         })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('overlay').style.display = 'none';
        sum_id += 1;
        const sumAudioPlayer = document.getElementById('sumAudioPlayer');
        sumAudioPlayer.src = `../static/files/${curUser}/${bookTitle}/sum_audio/q_${sum_id-1}.mp3`;
        sumAudioPlayer.play();
        document.getElementById('textInput').value = '';
        /* addStar(data); */
        if(data.end){
            document.getElementById('chatContent').innerHTML = `<p1>${data.feedback} </p1><p2>${data.explanation} </p2><p2>${data.transition} </p2>`;
            document.querySelector('.inputBlock').remove();
            /* document.querySelector('.submitBlock').remove(); */
        }
        else{
            document.getElementById('chatContent').innerHTML = `<p1>${data.feedback} </p1><p2>${data.explanation} </p2><p2>${data.transition} </p2></br><p3>${data.question} </p3>`;
        }
    })
    .catch(error => console.error('Error:', error));
}


function updateChatHistory(gptRes){
    /* 1. add the new QA in history
    2. record the answer (correct./incorrect), update dashboard
    3. If incorrect, show expanation and check*/
    var bg_color = '';
    if(gptRes.judgement == 'correct'){
        bg_color = '#eaf9e6';
    }
    else if(gptRes.judgement == 'incorrect') {
        bg_color = '#f4d6d2';
    }
    const history = document.querySelector('.chatHistory');
    QABlock = document.createElement('div');
    QABlock.className = 'QABlock';
    QABlock.innerHTML += `<div class="QAbubble" id="QAbubble_${gptRes.q_id}">
        <div class="message-system">
            <img src="../static/files/imgs/penguin.png" class="avatar">
            <div class="message-bubble sys">${curQA.question}</div>
        </div>
        <div class="message-user">
            <div class="message-bubble user" id="user_res_${gptRes.q_id}" style="background-color: ${bg_color}">${curQA.answer}</div>
            <img src="../static/files/imgs/EmmaIcon.png" class="avatar">
        </div>
    </div>`;
    /* if(!childRes.correct){
        QAbubble.innerHTML += `<div class="knowledgeDetail" id="kd${gptRes.q_id}">
            <p1>Question ${gptRes.q_id}</p1> </br>
            <p2>Knowledge: ${gptRes.knowledge}</p2> </br>
            <button class="closeButton" id="close${gptRes.q_id}" onclick='hideKnowledge(kd${gptRes.q_id})'>Close</button>
         </div>`
    } */
    history.appendChild(QABlock);
    /*QABlock.style.top = `${(history.children.length - 1)*60}px`;
    QABlock.style.zIndex = history.children.length;*/
    document.querySelector('.chatBox').scrollTop = history.scrollHeight;
}

function showQABubble(qId){
    const history = document.querySelector('.chatHistory');
    document.getElementById(`QAbubble_${qId}`).style.zIndex = history.children.length + 1;
}

function retainZIndex(zIndex, qId){
    document.getElementById(`QAbubble_${qId}`).style.zIndex = zIndex;
}

function addStar(response){
    const history = document.querySelector('.chatHistory');
    if(response.judgement == 'correct'){
        history.innerHTML += `<div class='starBlock'>
                                <img class='star' id="img${response.q_id}" onclick='showKnowledge(kd${response.q_id})' src='../static/files/imgs/star${response.q_id}.png'>
                                <div class="knowledgeDetail" id="kd${response.q_id}">
                                    <p1>Question ${response.q_id}</p1> </br>
                                    <p2>Knowledge: ${response.knowledge}</p2> </br>
                                    <button class="closeButton" id="close${response.q_id}" onclick='hideKnowledge(kd${response.q_id})'>Close</button>
                                </div>
                            </div>`;
    }
    else{
        history.innerHTML += `<div class='starBlock'>
                                <img class='prob' id="img${response.q_id}" onclick='showKnowledge(kd${response.q_id})' src='../static/files/imgs/question.png'>
                                <div class="knowledgeDetail" id="kd${response.q_id}">
                                    <p1>Question ${response.q_id}</p1> </br>
                                    <p2>Knowledge ${response.knowledge}</p2>
                                    <button id="learned" onclick='changeStar(img${response.q_id}, ${response.q_id})'>Now I get it!</button> </br>
                                    <button class="closeButton" id="close${response.q_id}" onclick='hideKnowledge(kd${response.q_id})'>Close</button>
                                </div>
                            </div>`;
    }
}

function showKnowledge(kdId){
    kdId.style.display = 'block';
}

function hideKnowledge(kdId){
    kdId.style.display = 'none';
}

function changeStar(imgId, qId){
    imgId.src = `../static/files/imgs/star${qId}.png`;
    document.getElementById('learned').remove();
    save_knowledge_state(false, 'false');
}

function save_knowledge_state(isClear, isEnd, callback){
    fetch('/api/continue', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            username: curUser,
            id: currentImageIndex-1,
            title: bookTitle,
            html: document.querySelector('.Knowledge').innerHTML,
            dash_stat_flag: isClear,
            end_flag: isEnd
         })
    })
    .then(response => response.json())
    .then(data => {
        if (isClear){
            document.querySelector('.container').removeChild(document.querySelector('.Knowledge'));
            console.log('kg cleared')
        }
        callback();
    })
    .catch(error => console.error('Error:', error));
}

function continueRead(){
    gptData[(currentImageIndex-1).toString()].answer = true;
    save_knowledge_state(true, 'false');

    audioPlayer.addEventListener('ended', playNextSentence);
    isKeyWord = false;
    NextPage();
}

function review(){
    console.log('review previous progress');
    isReview = false;
    fetch('/api/review', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            username: curUser,
            id: currentImageIndex-1,
            title: bookTitle
         })
    })
    .then(response => response.json())
    .then(data => {
        if(data == 'knowledge not saved'){
            console.log('knowledge not saved');
            genConv();
        }
        else{
            let knowledge = document.createElement("div");
            knowledge.className = 'Knowledge';
            knowledge.innerHTML = data;
            const container = document.querySelector('.container');
            if(container.children.length == 1){
                container.appendChild(knowledge);
            }
            isReview = true;
        }
    })
    .catch(error => console.error('Error:', error));
}



fetchGenData();

/* getUser(); */