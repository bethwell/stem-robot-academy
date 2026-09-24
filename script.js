/* ==========================================
   MiniMakers Robotics Academy
   Main JavaScript
========================================== */


/* ==========================================
   MOBILE MENU
========================================== */


const menuButton = document.querySelector(".mobile-menu");
const navLinks = document.querySelector(".nav-links");


if(menuButton){

    menuButton.addEventListener("click", ()=>{

        navLinks.classList.toggle("active");

    });

}



/* Close menu after clicking a link */

document.querySelectorAll(".nav-links a").forEach(link=>{

    link.addEventListener("click",()=>{

        navLinks.classList.remove("active");

    });

});



/* ==========================================
   STICKY HEADER
========================================== */


const header = document.getElementById("header");


window.addEventListener("scroll",()=>{


    if(window.scrollY > 50){

        header.classList.add("scrolled");

    }

    else{

        header.classList.remove("scrolled");

    }


});



/* ==========================================
   BACK TO TOP BUTTON
========================================== */


const backToTop = document.getElementById("backToTop");


window.addEventListener("scroll",()=>{


    if(window.scrollY > 500){

        backToTop.style.display="block";

    }

    else{

        backToTop.style.display="none";

    }


});



if(backToTop){


backToTop.addEventListener("click",()=>{


    window.scrollTo({

        top:0,

        behavior:"smooth"

    });


});


}



/* ==========================================
   SCROLL REVEAL ANIMATION
========================================== */


const revealElements = document.querySelectorAll(

    "section, .feature-card, .program-card, .stat"

);



const revealObserver = new IntersectionObserver(

(entries)=>{


entries.forEach(entry=>{


    if(entry.isIntersecting){


        entry.target.classList.add("show");


    }


});


},

{

    threshold:0.15

}

);



revealElements.forEach(element=>{


    element.classList.add("hidden");


    revealObserver.observe(element);


});





/* ==========================================
   NUMBER COUNTERS
========================================== */


const counters = document.querySelectorAll(".counter");


counters.forEach(counter=>{


    counter.innerText="0";


    const updateCounter=()=>{


        const target = +counter.getAttribute("data-target");


        const current = +counter.innerText;


        const increment = target / 100;



        if(current < target){


            counter.innerText=Math.ceil(current + increment);


            setTimeout(updateCounter,20);


        }


        else{


            counter.innerText=target;


        }


    };



    const counterObserver = new IntersectionObserver(entries=>{


        if(entries[0].isIntersecting){


            updateCounter();


            counterObserver.disconnect();


        }


    });



    counterObserver.observe(counter);



});





/* ==========================================
   SIMPLE TESTIMONIAL SLIDER
========================================== */


const testimonials = document.querySelectorAll(".testimonial");


let currentTestimonial = 0;



function showTestimonials(){


    testimonials.forEach(item=>{

        item.style.display="none";

    });



    if(testimonials.length > 0){


        testimonials[currentTestimonial].style.display="block";


        currentTestimonial++;



        if(currentTestimonial >= testimonials.length){

            currentTestimonial=0;

        }


    }


}



if(testimonials.length > 0){


    showTestimonials();


    setInterval(showTestimonials,5000);


}




/* ==========================================
   SMOOTH SCROLL LINKS
========================================== */


document.querySelectorAll('a[href^="#"]').forEach(anchor=>{


    anchor.addEventListener("click",function(e){


        const target=document.querySelector(
            this.getAttribute("href")
        );


        if(target){


            e.preventDefault();


            target.scrollIntoView({

                behavior:"smooth",

                block:"start"

            });


        }


    });


});



/* ==========================================
   PAGE LOAD EFFECT
========================================== */


window.addEventListener("load",()=>{


    document.body.classList.add("loaded");


});


/* ==========================================
   PROGRAM AUTO-SELECTION FOR CONTACT FORM
========================================== */

document.querySelectorAll(".program-join-btn").forEach(btn => {
    btn.addEventListener("click", function() {
        const actionName = this.getAttribute("data-program");
        
        // Find the subject input box inside your contact section
        const subjectInput = document.querySelector('form.contact-form input[placeholder*="Subject"]');
        
        if (subjectInput && actionName) {
            // Check the action name type to format the subject string perfectly
            if (actionName === "Free Demo Class") {
                subjectInput.value = `Requesting: ${actionName}`;
            } else if (actionName === "General Enrollment") {
                subjectInput.value = `Inquiry: ${actionName}`;
            } else {
                subjectInput.value = `Enrolling in: ${actionName}`;
            }
            
            // Give it a subtle background color shift to highlight the selection
            subjectInput.style.borderColor = "#ff8c00";
            subjectInput.style.backgroundColor = "#fff9f2";
        }
    });
});

/* ==========================================
   PRODUCTION WEB3FORMS CONTACT PROCESSOR
========================================== */
const contactForm = document.querySelector(".contact-form");

if (contactForm) {
    contactForm.addEventListener("submit", function (e) {
        e.preventDefault(); // Stop raw page redirects

        const formData = new FormData(contactForm);
        const submitButton = contactForm.querySelector('button[type="submit"]');
        const originalButtonText = submitButton.innerText;

        // UI processing indication
        submitButton.innerText = "Sending...";
        submitButton.disabled = true;

        const object = Object.fromEntries(formData);
        const json = JSON.stringify(object);

        fetch("https://api.web3forms.com/submit", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                Accept: "application/json"
            },
            body: json
        })
        .then(async (response) => {
            let res = await response.json();
            if (response.status === 200) {
                alert("Thank you! Your message has been sent successfully. We will get back to you shortly.");
                contactForm.reset(); // Wipe all form inputs clean
            } else {
                alert("Form Submission Issue: " + res.message);
            }
        })
        .catch((error) => {
            alert("Network connection error. Please verify your internet and try again.");
        })
        .then(() => {
            // Re-enable form button controls
            submitButton.innerText = originalButtonText;
            submitButton.disabled = false;
        });
    });
}