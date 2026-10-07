/* =========================================
   GET HTML ELEMENTS
========================================= */

const screenOne =
    document.getElementById("screenOne");

const screenTwo =
    document.getElementById("screenTwo");

const screenThree =
    document.getElementById("screenThree");

const screenFour =
    document.getElementById("screenFour");

const screenFive =
    document.getElementById("screenFive");


const yesButton =
    document.getElementById("yesButton");

const noButton =
    document.getElementById("noButton");


const continueButton =
    document.getElementById("continueButton");


const dateInput =
    document.getElementById("dateInput");

const dateButton =
    document.getElementById("dateButton");


const dateError =
    document.getElementById("dateError");


const foodButton =
    document.getElementById("foodButton");


const selectedDateText =
    document.getElementById("selectedDate");


const selectedFoodText =
    document.getElementById("selectedFood");


const foodOptions =
    document.querySelectorAll(".food-option");


/* =========================================
   VARIABLES
========================================= */

let selectedDate = "";

let selectedFood = "";

let responseSaved = false;


/* =========================================
   CHANGE SCREEN
========================================= */

function showScreen(screenToShow) {

    const allScreens = [
        screenOne,
        screenTwo,
        screenThree,
        screenFour,
        screenFive
    ];


    allScreens.forEach(function(screen) {

        screen.classList.remove("active");

    });


    screenToShow.classList.add("active");
}


/* =========================================
   SAVE RESPONSE TO DATABASE
========================================= */

async function saveResponse(
    answer,
    date,
    food
) {

    try {

        const response = await fetch(
            "/save-response",
            {
                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({

                    answer: answer,

                    selected_date: date,

                    selected_food: food

                })

            }
        );


        const data =
            await response.json();


        if (data.success) {

            responseSaved = true;

            console.log(
                "Response saved successfully."
            );

        }
        else {

            console.log(
                "Response was not saved."
            );

        }


    }
    catch (error) {

        console.error(
            "Database error:",
            error
        );

    }
}


/* =========================================
   YES BUTTON
========================================= */

yesButton.addEventListener(
    "click",
    function() {

        showScreen(screenTwo);

    }
);


/* =========================================
   NO BUTTON
   MOVES AWAY WHEN CLICKED
========================================= */

noButton.addEventListener(
    "mouseenter",
    function() {

        moveNoButton();

    }
);


noButton.addEventListener(
    "touchstart",
    function(event) {

        event.preventDefault();

        moveNoButton();

    }
);


noButton.addEventListener(
    "click",
    function(event) {

        event.preventDefault();

        moveNoButton();

    }
);


/* =========================================
   MOVE NO BUTTON
========================================= */

function moveNoButton() {

    const card =
        document.getElementById("dateCard");


    const cardRect =
        card.getBoundingClientRect();


    const buttonRect =
        noButton.getBoundingClientRect();


    const maxX =
        cardRect.width -
        buttonRect.width -
        20;


    const maxY =
        cardRect.height -
        buttonRect.height -
        20;


    const randomX =
        Math.random() * maxX -
        (cardRect.width / 2) +
        (buttonRect.width / 2);


    const randomY =
        Math.random() * maxY -
        (cardRect.height / 2) +
        (buttonRect.height / 2);


    noButton.style.position =
        "relative";


    noButton.style.left =
        randomX + "px";


    noButton.style.top =
        randomY + "px";


    noButton.style.transition =
        "all 0.25s ease";


    noButton.textContent =
        "NO 😭";
}


/* =========================================
   SECOND SCREEN
========================================= */

continueButton.addEventListener(
    "click",
    function() {

        showScreen(screenThree);

    }
);


/* =========================================
   DATE BUTTON
========================================= */

dateButton.addEventListener(
    "click",
    function() {

        if (
            dateInput.value === ""
        ) {

            dateError.textContent =
                "Please choose a date first 💕";

            return;

        }


        selectedDate =
            dateInput.value;


        dateError.textContent =
            "";


        showScreen(screenFour);

    }
);


/* =========================================
   FOOD OPTIONS
========================================= */

foodOptions.forEach(
    function(option) {

        option.addEventListener(
            "click",
            function() {

                foodOptions.forEach(
                    function(item) {

                        item.classList.remove(
                            "selected"
                        );

                    }
                );


                option.classList.add(
                    "selected"
                );


                selectedFood =
                    option.getAttribute(
                        "data-food"
                    );

            }
        );

    }
);


/* =========================================
   FOOD BUTTON
========================================= */

foodButton.addEventListener(
    "click",
    async function() {

        if (
            selectedFood === ""
        ) {

            alert(
                "Please choose something to eat 😋"
            );

            return;

        }


        selectedDateText.textContent =
            selectedDate;


        selectedFoodText.textContent =
            selectedFood;


        /*
         * Save the YES response only
         * after the person completes
         * the date and food selection.
         */

        if (!responseSaved) {

            await saveResponse(
                "YES",
                selectedDate,
                selectedFood
            );

        }


        showScreen(screenFive);

    }
);