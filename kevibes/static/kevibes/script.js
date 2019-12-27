let navbar = document.querySelector('#side-nav')


showAlert = (message, theme, duration, fade_action) => {
    if (!document.querySelector('.message-box')){ // if not present 
        let div = document.createElement('div');
        div.className = `message-box bg-${theme} wow ${fade_action}`;
        div.appendChild(document.createTextNode(message));
        document.body.appendChild(div);
        document.documentElement.scrollTo(0,0);
        setTimeout(() => {
            div.style.visibility = '';
        }, duration);
        // setTimeout(() => { div.classList.remove('wow'); document.body.removeChild(div); }, duration);
    }else{ // if present 
        document.body.removeChild(document.querySelector('.message-box'));
        let div = document.createElement('div');
        div.className = `message-box bg-${theme} wow ${fade_action}`;
        div.appendChild(document.createTextNode(message));
        document.body.appendChild(div);
        document.documentElement.scrollTo(0,0);
        setTimeout(() => {
            div.style.visibility = '';
        }, duration);
        // setTimeout(() => { div.classList.remove('wow'); document.body.removeChild(div); }, duration);
    }
}


let handleControls = (song, button, btnsList, songsList, fontSize) => { // the font size parameter is to control the size of the fa play, pause icon
    if (!button.classList.contains('played')){
        // console.log("playing");
        btnsList.forEach((btn, pos) => { // this section is to iterate through all songs and pause any one playing
            btn.classList.remove('played'); // and then play the one that was just on 
            btn.innerHTML = '';
            btn.innerHTML += `<i class="fas fa-play-circle ${fontSize}">`;
            btn.appendChild(songsList[pos]);
            songsList[pos].pause();
        });
        button.innerHTML = '';
        button.innerHTML += `<i class="fas fa-pause-circle ${fontSize}">`;
        button.appendChild(song);
        button.classList.remove('paused')
        button.classList.add('played');
        song.play();
    }else{
        // console.log("pausing");
        button.innerHTML = '';
        button.innerHTML += `<i class="fas fa-play-circle ${fontSize}">`;
        button.appendChild(song);
        button.classList.remove('played');
        button.classList.add('paused');
        song.pause();
    }
}
