const queryString = window.location.search;
const urlParams = new URLSearchParams(queryString);

const bookTitle = decodeURIComponent(urlParams.get('title'));
/* document.getElementById('BookTitle').innerHTML = bookTitle; */

var blank_persona = {
    isFill: 0,
    isSkip: 0,
    age: "",
    name: "",
    hobby: "",
    science: ""
};

var curUser = document.getElementById('Profile').textContent;

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
        getPersona();
    })
    .catch((error) => {
        console.error('Error get user information:', error);
    });
}


function toggleAgeSelector() {
    const ageSelector = document.getElementById('ageSelector');
    ageSelector.style.display = ageSelector.style.display === 'block' ? 'none' : 'block';
}

function selectAge(age) {
    document.getElementById('selectedAge').textContent = age;
    document.getElementById('ageSelector').style.display = 'none';
}

function toggleOtherInput(inputId) {
    const otherInput = document.getElementById(inputId);
    otherInput.style.display = otherInput.style.display === 'none' ? 'inline-block' : 'none';
}


function submitAnswers() {
    const answer1 = document.getElementById('question1').value;
    const selectedAge = document.getElementById('selectedAge').textContent;
    const answer3 = document.querySelector('input[name="question3"]:checked');
    const answer3Other = document.getElementById('question3OtherInput').value;
    const answer4 = document.querySelector('input[name="question4"]:checked');
    const answer4Other = document.getElementById('question4OtherInput').value;

    let answer3Text = answer3 ? answer3.value : '';
    if (answer3Text === '其他') {
        answer3Text = answer3Other;
    }

    let answer4Text = answer4 ? answer4.value : '';
    if (answer4Text === '其他') {
        answer4Text = answer4Other;
    }

    let persona = {
        isFill: 0,
        age: "",
        name: "",
        hobby: "",
        science: ""
    };

    persona.name = answer1;
    persona.age = selectedAge;
    persona.hobby = answer3Text;
    persona.science = answer4Text;
    persona.isFill = 1;
    
    console.log(persona);
    send_info(persona);
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
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}


function send_info(persona_dict){
    fetch('/api/personaUpdate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
            username: curUser,
            title: bookTitle,
            persona: persona_dict
        }),
    })
    .then(response => response.json())
    .then(data => {
        window.location.href = './bookDetail?title=' + encodeURIComponent(bookTitle); 
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}

function skip_info(){
    let skip_persona = blank_persona
    skip_persona.isSkip = 1;
    send_info(skip_persona);
}

getUser();