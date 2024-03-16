const usernameField = document.querySelector("#usernameField");
const FeedbackArea = document.querySelectorAll(".invalid_feedback");
const emailField = document.querySelector("#emailField");
const passwordField = document.querySelector("#passwordField");
const EmailFeedBack = document.querySelectorAll(".email_feedback");
// const usernamecheck = document.querySelector(".usernamecheck");
const showpasswordToggle = document.querySelector(".showpasswordToggle");
// submit button changes
const submitbutton = document.querySelector(".submit-btn");

// Password Toggle
const handleToggle = (e) =>{
    if(showpasswordToggle.textContent === "SHOW"){
        showpasswordToggle.textContent = "HIDE";
        passwordField.setAttribute("type","text");
    }
    else{
        showpasswordToggle.textContent = "SHOW";
        passwordField.setAttribute("type","password");
    }
};
showpasswordToggle.addEventListener("click", handleToggle);




// Username vaidation
usernameField.addEventListener("keyup", (e)=>{
    const userVal = e.target.value;
    // usernamecheck.textContent = `Checking ${userVal}`;
    usernameField.classList.remove("is-invalid");
    FeedbackArea[0].style.display = "none";
    // usernamecheck.style.display = "block";
    if(userVal.length>0){
        fetch("/authentication/validate-username",{
            body:JSON.stringify({username:userVal}),
            method:"POST",
        })
        .then((res)=>res.json())
        .then((data)=>{
            console.log("data",data);
            if(data.username_error){
                usernameField.classList.add("is-invalid");
                // usernamecheck.textContent = "";
                FeedbackArea[0].style.display = "block";
                // usernamecheck.style.display = "none";
                FeedbackArea[0].innerHTML = `<p> ${data.username_error} </p>`
                //disable submit button
                submitbutton.disabled = true
            }
            else{
                submitbutton.removeAttribute("disabled")
            }
        })
    }
});


// Email Validater
emailField.addEventListener("keyup", (e)=>{
    const emailVal = e.target.value;
    emailField.classList.remove("is-invalid");
    EmailFeedBack[0].style.display = "none";
    if(emailVal.length>0){
        fetch("/authentication/validate-email",{
            body:JSON.stringify({email:emailVal}),
            method:"POST",
        })
        .then((res)=>res.json())
        .then((data)=>{
            console.log("data",data);
            if(data.email_error){
                emailField.classList.add("is-invalid");
                EmailFeedBack[0].style.display = "block";
                EmailFeedBack[0].innerHTML = `<p> ${data.email_error} </p>`
                submitbutton.disabled = true
            }
            else{
                submitbutton.removeAttribute("disabled")
            }
        })
    }
});