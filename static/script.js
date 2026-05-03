function buildQuestionBlock(index) {
    return `
        <section class="manager-question-block">
            <h2>Question ${index}</h2>
            <label for="question_text_${index}">Question</label>
            <textarea id="question_text_${index}" name="question_text_${index}" placeholder="Enter CBSE Computer Science question"></textarea>

            <label for="option_a_${index}">Option A</label>
            <input id="option_a_${index}" name="option_a_${index}" type="text">

            <label for="option_b_${index}">Option B</label>
            <input id="option_b_${index}" name="option_b_${index}" type="text">

            <label for="option_c_${index}">Option C</label>
            <input id="option_c_${index}" name="option_c_${index}" type="text">

            <label for="option_d_${index}">Option D</label>
            <input id="option_d_${index}" name="option_d_${index}" type="text">

            <label for="correct_answer_${index}">Correct answer</label>
            <select id="correct_answer_${index}" name="correct_answer_${index}">
                <option value="A">A</option>
                <option value="B">B</option>
                <option value="C">C</option>
                <option value="D">D</option>
            </select>

            <label for="solution_${index}">Solution</label>
            <textarea id="solution_${index}" name="solution_${index}" placeholder="Explain the correct option and concept"></textarea>
        </section>
    `;
}

const questionCountInput = document.querySelector("[data-question-count]");
const questionBlocks = document.querySelector("#questionBlocks");

if (questionCountInput && questionBlocks) {
    questionCountInput.addEventListener("input", () => {
        const count = Math.min(Math.max(Number(questionCountInput.value || 0), 1), 50);
        let currentCount = questionBlocks.querySelectorAll(".manager-question-block").length;

        while (currentCount > count) {
            questionBlocks.lastElementChild.remove();
            currentCount -= 1;
        }

        for (let index = currentCount + 1; index <= count; index += 1) {
            questionBlocks.insertAdjacentHTML("beforeend", buildQuestionBlock(index));
        }
    });
}

const examForm = document.querySelector("[data-exam-form]");

if (examForm) {
    const questions = Array.from(document.querySelectorAll("[data-exam-question]"));
    const paletteButtons = Array.from(document.querySelectorAll("[data-jump-question]"));
    const previousButton = document.querySelector("[data-prev-question]");
    const nextButton = document.querySelector("[data-next-question]");
    const skipButton = document.querySelector("[data-skip-question]");
    const attemptedCount = document.querySelector("[data-attempted-count]");
    const remainingCount = document.querySelector("[data-remaining-count]");
    const skippedCount = document.querySelector("[data-skipped-count]");
    const timerBox = document.querySelector("[data-exam-minutes]");
    const timerDisplay = document.querySelector("[data-timer-display]");
    const skippedQuestions = new Set();
    let currentIndex = 0;

    function questionAnswered(question) {
        return Boolean(question.querySelector("input[type='radio']:checked"));
    }

    function updatePalette() {
        let attempted = 0;

        questions.forEach((question, index) => {
            const questionId = question.dataset.questionId;
            const paletteButton = paletteButtons[index];
            const answered = questionAnswered(question);

            if (answered) {
                attempted += 1;
                skippedQuestions.delete(questionId);
            }

            paletteButton.classList.toggle("answered", answered);
            paletteButton.classList.toggle("skipped", !answered && skippedQuestions.has(questionId));
            paletteButton.classList.toggle("current", index === currentIndex);
        });

        attemptedCount.textContent = attempted;
        remainingCount.textContent = questions.length - attempted;
        skippedCount.textContent = skippedQuestions.size;
    }

    function showQuestion(index) {
        currentIndex = Math.min(Math.max(index, 0), questions.length - 1);
        questions.forEach((question, questionIndex) => {
            question.classList.toggle("is-hidden", questionIndex !== currentIndex);
        });
        previousButton.disabled = currentIndex === 0;
        nextButton.disabled = currentIndex === questions.length - 1;
        updatePalette();
    }

    previousButton.addEventListener("click", () => showQuestion(currentIndex - 1));
    nextButton.addEventListener("click", () => showQuestion(currentIndex + 1));
    skipButton.addEventListener("click", () => {
        const currentQuestion = questions[currentIndex];

        if (!questionAnswered(currentQuestion)) {
            skippedQuestions.add(currentQuestion.dataset.questionId);
        }

        showQuestion(currentIndex + 1);
    });

    paletteButtons.forEach((button) => {
        button.addEventListener("click", () => showQuestion(Number(button.dataset.jumpQuestion)));
    });

    examForm.addEventListener("change", (event) => {
        if (event.target.matches("input[type='radio']")) {
            updatePalette();
        }
    });

    if (timerBox && timerDisplay) {
        let remainingSeconds = Number(timerBox.dataset.examMinutes || 0) * 60;

        const tick = () => {
            const minutes = Math.floor(remainingSeconds / 60);
            const seconds = remainingSeconds % 60;
            timerDisplay.textContent = `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;

            if (remainingSeconds <= 0) {
                examForm.submit();
                return;
            }

            remainingSeconds -= 1;
            window.setTimeout(tick, 1000);
        };

        tick();
    }

    showQuestion(0);
}
