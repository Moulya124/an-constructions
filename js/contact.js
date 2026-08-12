document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("contactForm");

    if (!form) {
        return;
    }

    const status = document.getElementById("formStatus");
    const button = document.getElementById("submitBtn");

    /*
     * FormSubmit handles the actual email submission.
     *
     * This JavaScript only:
     * - validates the form
     * - shows "Sending..."
     * - prevents double-clicks
     *
     * It does NOT call /api/contact.
     */

    form.addEventListener("submit", (event) => {

        if (!form.checkValidity()) {
            event.preventDefault();
            form.reportValidity();
            return;
        }

        if (button) {
            button.disabled = true;
            button.textContent = "Sending...";
        }

        if (status) {
            status.className = "form-status";
            status.textContent = "Sending your enquiry...";
        }

        /*
         * IMPORTANT:
         * Do NOT call event.preventDefault() here.
         *
         * The normal form submission goes to:
         * https://formsubmit.co/your-email
         *
         * FormSubmit then sends the enquiry by email.
         */
    });
});