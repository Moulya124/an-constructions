document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("contactForm");
  if (!form) return;

  const status = document.getElementById("formStatus");
  const button = document.getElementById("submitBtn");

  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    if (!form.checkValidity()) {
      form.reportValidity();
      return;
    }

    const payload = Object.fromEntries(new FormData(form).entries());
    button.disabled = true;
    button.textContent = "Sending...";
    status.className = "form-status";
    status.textContent = "";

    try {
      const response = await fetch("/api/contact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      const result = await response.json();

      if (!response.ok || !result.success) {
        throw new Error(result.message || "Unable to send your enquiry.");
      }

      status.className = "form-status success";
      status.textContent = "Thank you! Your enquiry has been submitted successfully.";
      form.reset();
    } catch (error) {
      status.className = "form-status error";
      status.textContent = error.message || "Something went wrong. Please try again.";
    } finally {
      button.disabled = false;
      button.textContent = "Send Enquiry →";
    }
  });
});

