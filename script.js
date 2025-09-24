let sections = document.querySelectorAll('section');
let navlinks = document.querySelectorAll('header nav a');

// Navbar link active on scroll
window.onscroll = () => {
    sections.forEach(sec => {
        let top = window.scrollY;
        let offset = sec.offsetTop - 150;
        let height = sec.offsetHeight;
        let id = sec.getAttribute('id');

        if (top >= offset && top < offset + height) {
            navlinks.forEach(links => {
                links.classList.remove('active');
                document.querySelector('header nav a[href*=' + id + ']').classList.add('active');
            });
        }
    });

    let header = document.querySelector('header');
    header.classList.toggle('sticky', window.scrollY > 100);

    // Close navbar after clicking link
    menuIcon.classList.remove('bx-x');
    navbar.classList.remove('active');
};

// Toggle Navbar Menu
let menuIcon = document.querySelector('#menu-icon');
let navbar = document.querySelector('.navbar');

menuIcon.onclick = () => {
    menuIcon.classList.toggle('bx-x');
    navbar.classList.toggle('active');
};

// Scroll Reveal Animations
ScrollReveal({
    reset: true,
    distance: '80px',
    duration: 2000,
    delay: 200
});

ScrollReveal().reveal('.home-content, .heading', {origin: 'top'});
ScrollReveal().reveal('.home-img, .services-container, .portfolio-box, .contact form', {origin: 'bottom'});
ScrollReveal().reveal('.home-content h1, .about-img', {origin: 'left'});
ScrollReveal().reveal('.home-content p, .about-content', {origin: 'right'});


function startAssistant() {
    const userInput = document.getElementById("userInput").value;

    fetch("http://localhost:5000/process", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({input: userInput})
    })
        .then(response => response.json())
        .then(data => {
            const cevapDiv = document.getElementById("cevapDiv");

            //  Kategori ve Alt Kategori ayrı ayrı
            cevapDiv.innerHTML = `
            <div class="kategori-bilgi">
                <span>
                <h3 class="kategori">En iyi kategori: <strong>${data.category}</strong></h3>
                </span>
                <span>
                <h3 class="alt-kategori">Alt kategori: <strong>${data.subcategory}</strong></h3>
                </span>
            </div>
        `;


            if (data.products.length > 0) {
                cevapDiv.innerHTML += `

                <div class="recommendation-container">
                    ${data.products.map(product => `
                        <div class="product-card">
                            <h4>${product}</h4>
                        </div>
                    `).join('')}
                </div>
            `;
            } else {
                cevapDiv.innerHTML += `<h3 class="output-title">${data.message}</h3>`;
            }

            // Scroll yukarı
            document.getElementById("home").scrollIntoView({behavior: "smooth"});
        })
        .catch(error => {
            console.error("Error:", error);
        });
}


