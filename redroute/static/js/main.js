let menu = document.querySelector('#menu-icon');
let navlist = document.querySelector('.navlist');
let navbar = document.querySelector('.nav-el');

window.onscroll = () => {
    if (window.scrollY > 20 && window.innerWidth > 768) {
        navbar.classList.add('fixed');
    }
    else {
        navbar.classList.remove('fixed');
    }
}

menu.onclick = () => {
    menu.classList.toggle('bx-x');
    navlist.classList.toggle('open');
}
