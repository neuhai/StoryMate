const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);
const bookTitle = decodeURIComponent(urlParams.get('title'));

let id = 2;
var isConvPlayed = false;
var curUser = '';

localStorage.clear()

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
        if(persona.isFill == 1){
            window.location.href= './bookRead?title=' + encodeURIComponent(bookTitle); 
        }
        else{
            genGreet();
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
        console.log(curUser);
        getPersona();
    })
    .catch((error) => {
        console.error('Error get user information:', error);
    });
}

function genGreet(){
    fetch('/api/greet', {
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

        let chatBox = document.createElement("div");
        chatBox.className = 'chatBox';
        document.getElementById('chatContent').innerHTML = `<p1>${data} </p1>`;
        if(document.querySelector('.inputBlock')){
            return;
        }
        document.querySelector('.chatBox').innerHTML += `<div class='inputBlock'>
                                <div id="overlay"></div>
                                <textarea id="textInput"></textarea>
                                <button id="voiceInputBtn" onclick="toggleVoiceInput()">
                                    <img src='../static/files/imgs/voiceInput.png'>点击按钮开始回答！
                                </button>
                                <img id='loading' src="../static/files/imgs/loading.gif">
                              </div>`
        console.log(isConvPlayed);
        if(!isConvPlayed){
            document.getElementById('convAudioPlayer').addEventListener('ended', function () {
                isConvPlayed = true;
            });
            /* playConvAudio(); */
            playConvAudio(`../static/files/${curUser}/greet_audio/q_1.mp3`);
        }
    })
    .catch(error => console.error('Error:', error));
}

function submitText() {
    isConvPlayed = false;
    const textInput = document.getElementById('textInput');
    document.getElementById('loading').style.display = 'block';
    document.getElementById('overlay').style.display = 'block';
    /* if(textInput.value == ''){
        alert("You need to answer this question first!");
        return;
    } */
    console.log(textInput.value)
    fetch('/api/answer', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ 
            username: curUser,
            id: id.toString(),
            title: bookTitle,
            response: textInput.value,
         })
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('loading').style.display = 'none';
        document.getElementById('overlay').style.display = 'none';
        id += 1;
        console.log(data);

        const convAudioPlayer = document.getElementById('convAudioPlayer');
        convAudioPlayer.src = `../static/files/${curUser}/greet_audio/q_${id-1}.mp3`;
        convAudioPlayer.play();
        document.getElementById('textInput').value = '';
        /* addStar(data); */
        if('end' in data){
            document.getElementById('chatContent').innerHTML = `<p1>${data.greeting_content} </p1>`;
            document.querySelector('.inputBlock').remove();


            const button = document.createElement('button');
            button.id = 'beginRead';
            button.innerText = '开始阅读！';
            button.onclick = function() {
                window.location.href='./bookRead?title=' + encodeURIComponent(bookTitle);
            };
            document.querySelector('.uploadBlock').appendChild(button);
        }
        else{
            document.getElementById('chatContent').innerHTML = `<p1>${data.greeting_content} </p1>`;
        }
    })
    .catch(error => console.error('Error:', error));
}


let recognition;
let recognizing = false;

function toggleVoiceInput() {
    const textInput = document.getElementById('textInput');
    const voiceInputBtn = document.getElementById('voiceInputBtn');

    if (recognizing) {
        // Stop recognition
        recognition.stop();
        recognizing = false;
        voiceInputBtn.innerHTML = `<img src='../static/files/imgs/voiceInput.png'>点击按钮开始回答！`;
        submitText();
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

function playConvAudio(audioSrc) {
    isAudioEnded = false;
    const convAudioPlayer = document.getElementById('convAudioPlayer');
    convAudioPlayer.src = audioSrc;
    convAudioPlayer.play();
}

getUser();