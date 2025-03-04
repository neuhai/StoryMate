const books1 = [
    //{ title: "The Little Snowplow", subDis: ['Motion and Stability', 'Engineering Design', 'Earth’s Systems'] },
    //{ title: "Newton And Me", subDis: ['Motion and Stability', 'Engineering Design', 'Earth’s Systems'] },
    { title: "Oscar and the CRICKET", subDis: ['Motion and Stability', 'Engineering Design', 'Earth’s Systems'] },
    // Add more books as needed
];

const books2 = [
    //{ title: `Sami\'s Beach Rescue`, subDis: ['Earth’s Systems', 'Motion and Stability', 'Biological Evolution'] },
    { title: "你想种什么", subDis: ['生态系统'] },
    { title: `Amara and the Bats`, subDis: ['Earth’s Systems', 'Motion and Stability', 'Biological Evolution'] },
    // Add more books as needed
];

const books3 = [
    //{ title: "How to Catch the Wind", subDis: ['Earth’s Systems', 'Motion and Stability'] },
    //{ title: "Why Do Sunflowers Love the Sun", subDis: ['Earth’s Systems', 'Energy', "Earth’s Place in the Universe"] }
    { title: "海边度假", subDis: ['地球系统'] },
    { title: "Fairy Science", subDis: ['Earth’s Systems', 'Motion and Stability'] },
    // Add more books as needed
];

const books4 = [
    //{ title: "How to Catch the Wind", subDis: ['Earth’s Systems', 'Motion and Stability'] },
    //{ title: "Why Do Sunflowers Love the Sun", subDis: ['Earth’s Systems', 'Energy', "Earth’s Place in the Universe"] }
    { title: "PENNY, the Engineering Tail of the Fourth Little Pig", subDis: ['Earth’s Systems', 'Motion and Stability'] },
    // Add more books as needed
];


const shelf1 = document.getElementById('Shelf1')
const shelf2 = document.getElementById('Shelf2')
const shelf3 = document.getElementById('Shelf3')
const shelf4 = document.getElementById('Shelf4')
var curUser = '';

function getTag(dis){
    var topics = [
        "Motion and Stability", "Biological Evolution", "Earth’s Systems", "Engineering Design", "Energy", "Earth’s Place in the Universe"
    ]
    if(dis=="地球系统"){
        return 3;
    }
    return topics.indexOf(dis) + 1
}

books1.map((book, index) => {
    const bookElement = document.createElement('div');
    bookElement.innerHTML = `
    <div class='FeaturedBook' key=${index} onclick="toGreeting('${book.title}')">
        <img src='../static/files/books/${encodeURIComponent(book.title).replace(/'/g, '%27')}/cover.jpg' alt=${book.title} />
        
        <div class='ShelfBookTitle'>${book.title}</div>
        <div class='tagSpace' id='tags_1${index}'>
        </div>
        
        <div class='ShelfReadBook'>
            <i class="fa-solid fa-forward"></i>
            阅读这本书
        </div>
    </div>`
    shelf1.appendChild(bookElement);
    document.getElementById(`tags_1${index}`).innerHTML = '';
    for(let dis in book.subDis){
        document.getElementById(`tags_1${index}`).innerHTML += `<div class='tag${getTag(book.subDis[dis])}'>#${book.subDis[dis]}</div>`;
    }
});

books2.map((book, index) => {
    const bookElement = document.createElement('div');
    bookElement.innerHTML = `
    <div class='FeaturedBook' key=${index} onclick="toGreeting('${encodeURIComponent(book.title).replace(/'/g, '%27')}')">
        <img src='../static/files/books/${encodeURIComponent(book.title).replace(/'/g, '%27')}/cover.jpg' alt=${book.title} />

        <div class='ShelfBookTitle'>${book.title}</div>
        <div class='tagSpace' id='tags_2${index}'>
        </div>

        <div class='ShelfReadBook'>
            <i class="fa-solid fa-forward"></i>
            阅读这本书
        </div>
    </div>`
    shelf2.appendChild(bookElement);
    document.getElementById(`tags_2${index}`).innerHTML = '';
    for(let dis in book.subDis){
        document.getElementById(`tags_2${index}`).innerHTML += `<div class='tag${getTag(book.subDis[dis])}'>#${book.subDis[dis]}</div>`;
    }
});

books3.map((book, index) => {
    const bookElement = document.createElement('div');
    bookElement.innerHTML = `
    <div class='FeaturedBook' key=${index} onclick="toGreeting('${book.title}')">
        <img src='../static/files/books/${encodeURIComponent(book.title).replace(/'/g, '%27')}/cover.jpg' alt=${book.title} />

        <div class='ShelfBookTitle' >${book.title}</div>
        <div class='tagSpace' id='tags_3${index}'>
        </div>

        <div class='ShelfReadBook'>
            <i class="fa-solid fa-forward"></i>
            阅读这本书
        </div>
    </div>`
    shelf3.appendChild(bookElement);
    document.getElementById(`tags_3${index}`).innerHTML = '';
    for(let dis in book.subDis){
        document.getElementById(`tags_3${index}`).innerHTML += `<div class='tag${getTag(book.subDis[dis])}'>#${book.subDis[dis]}</div>`;
    }
});

books4.map((book, index) => {
    const bookElement = document.createElement('div');
    bookElement.innerHTML = `
    <div class='FeaturedBook' key=${index} onclick="toGreeting('${book.title}')">
        <img src='../static/files/books/${encodeURIComponent(book.title).replace(/'/g, '%27')}/cover.jpg' alt=${book.title} />

        <div class='ShelfBookTitle'>${book.title}</div>
        <div class='tagSpace' id='tags_4${index}'>
        </div>

        <div class='ShelfReadBook'>
            <i class="fa-solid fa-forward"></i>
            阅读这本书
        </div>
    </div>`
    shelf4.appendChild(bookElement);
    document.getElementById(`tags_4${index}`).innerHTML = '';
    for(let dis in book.subDis){
        document.getElementById(`tags_4${index}`).innerHTML += `<div class='tag${getTag(book.subDis[dis])}'>#${book.subDis[dis]}</div>`;
    }
});

function toBookRead(title){
    window.location.href='./bookRead?title=' + encodeURIComponent(title);
}

function toGreeting(title){
    window.location.href='./greeting?title=' + encodeURIComponent(title);
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
    })
    .catch((error) => {
        console.error('Error get user information:', error);
    });
}

/* getUser(); */