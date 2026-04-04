function toggleDark() {

    document.body.classList.toggle("dark");

    if (document.body.classList.contains("dark")) {

        localStorage.setItem("theme", "dark");

    } else {

        localStorage.setItem("theme", "light");

    }

}

window.onload = function() {

    const theme = localStorage.getItem("theme");

    if (theme === "dark") {

        document.body.classList.add("dark");

    }

}

function sortResults(type) {

    let container = document.querySelector(".showcase-grid");

    if (!container) return;

    let cards = Array.from(container.querySelectorAll(".showcase-card"));

    cards.sort((a, b) => {

        if (type === "match") { 
            return b.dataset.score - a.dataset.score;
        }
        if (type === "price") {
            return a.dataset.price - b.dataset.price;
        }
        if (type === "size") {
            return b.dataset.size - a.dataset.size;
        }
        return 0;

    });

    cards.forEach(card => container.appendChild(card));

    updateShowcaseClasses();

}

function updateShowcaseClasses() {
   const cards = document.querySelectorAll(".showcase-card");
   cards.forEach((card, index) => {
       card.classList.remove("featured", "side");
       if (index === 1) {
           card.classList.add("featured");
       } else {
           card.classList.add("side");
       }
   });
}

function moveShowcase(direction) {
   const container = document.querySelector(".showcase-grid");
   if (!container) return;
   const cards = Array.from(container.querySelectorAll(".showcase-card"));
   if (cards.length < 2) return;
   if (direction === "next") {
       container.appendChild(cards[0]);
   } else if (direction === "prev") {
       container.insertBefore(cards[cards.length - 1], cards[0]);
   }
   updateShowcaseClasses();

}

function toggleFilters() {

    const panel = document.getElementById("filters-panel");

    if (panel) {

        panel.classList.toggle("open");

    }
}

document.addEventListener("DOMContentLoaded", () => {
   updateShowcaseClasses();
   const leftArrow = document.querySelector(".left-arrow");
   const rightArrow = document.querySelector(".right-arrow");
   if (leftArrow) {
       leftArrow.addEventListener("click", () => moveShowcase("prev"));
   }
   if (rightArrow) {
       rightArrow.addEventListener("click", () => moveShowcase("next"));
   }

});

document.addEventListener("DOMContentLoaded", () => {
    const loader = document.getElementById("ai-loading");
    const results = document.querySelector(".showcase-wrapper");

    if (loader && results) {
        results.style.display = "none";
        setTimeout(() => {
            loader.style.display = "none";
            results.style.display = "block";
        }, 1200);
    }
});
document.addEventListener("DOMContentLoaded", function () {
   const btn = document.getElementById("scroll-to-search");
   const section = document.getElementById("search-section");
   const input = document.getElementById("dream-home-input");
   if (btn && section && input) {
       btn.addEventListener("click", function (e) {
           e.preventDefault();
           section.scrollIntoView({
               behavior: "smooth",
               block: "center"
           });
           setTimeout(() => {
               input.removeAttribute("readonly");
               input.focus({ preventScroll: true });
               input.select();
           }, 900);
       });
   }
});
document.addEventListener("DOMContentLoaded", function () {
   const btn = document.getElementById("scroll-to-search");
   const section = document.getElementById("search-section");
   const input = document.getElementById("dream-home-input");
   if (btn && section && input) {
       btn.addEventListener("click", function () {
           section.scrollIntoView({
               behavior: "smooth",
               block: "center"
           });
           setTimeout(() => {
               input.focus();
               input.select();
           }, 900);
       });
   }
});
document.addEventListener("DOMContentLoaded", function () {
 const form = document.querySelector('.ai-search-card form');
 const submitBtn = document.querySelector('.ai-search-submit');
 if (form && submitBtn) {
   form.addEventListener("submit", function (e) {
     e.preventDefault();
     submitBtn.disabled = true;
     submitBtn.innerHTML = "Analysere <span class='spinner'></span>";
     setTimeout(function () {
       form.submit();
     }, 1200);
   });
 }
 const resultsSection = document.getElementById("results-section");
 if (resultsSection) {
   resultsSection.scrollIntoView({ behavior: "smooth" });
 }
});

document.addEventListener("DOMContentLoaded", () => {
    const homeLink = document.getElementById("home-link");
    if (homeLink) {
        homeLink.addEventListener("click", (e) => {
            if (window.location.pathname === "/") {
                e.preventDefault();
                window.scrollTo({ top: 0, behavior: "smooth" });
            }
        });
    }
});