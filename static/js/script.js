document.addEventListener("DOMContentLoaded", () => {
  const signupForm = document.getElementById("signup-form");
  const signupErrorMsg = document.getElementById("signup-error-message");
  if (!signupForm || !signupErrorMsg) return;

  signupForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    signupErrorMsg.textContent = "";

    const submitBtn = document.getElementById("signup-submit");
    if (!submitBtn) {
      console.error("Missing #signup-submit button");
      return;
    }

    const originalText = submitBtn.textContent;
    submitBtn.disabled = true;

    const data = {
      name: (document.getElementById("name")?.value || "").trim(),
      email: (document.getElementById("email")?.value || "").trim().toLowerCase(),
      mobile: document.getElementById("mobile")?.value.trim() || "",
      password: document.getElementById("password")?.value || ""
    };

    try {
      const res = await fetch("/api/signup", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
      });
      const result = await res.json();

      if (res.ok) {
        const modalEl = document.getElementById("successModal");
        if (modalEl) {
          new bootstrap.Modal(modalEl).show();
          setTimeout(() => (window.location.href = "/login"), 2000);
        } else {
          console.warn("#successModal not found, redirecting immediately");
          window.location.href = "/login";
        }
      } else {
        signupErrorMsg.textContent = result.error || "Signup failed!";
      }
    } catch (err) {
      console.error("Signup error:", err);
      signupErrorMsg.textContent = err.message || "Signup failed unexpectedly.";
    } finally {
      submitBtn.disabled = false;
      submitBtn.textContent = originalText;
    }
  });
});

// login
const loginForm = document.getElementById("login-form");
const loginErrorMsg = document.getElementById("login-error-message");
const loginModal = document.getElementById("login-success-modal");

if (loginForm) {
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    loginErrorMsg.textContent = "";
    const submitBtn = document.getElementById("login-submit");
    const originalBtnText = submitBtn.textContent;
    submitBtn.disabled = true;
    submitBtn.textContent = "Logging in…";

    const data = {
      identifier: document.getElementById("identifier").value.trim().toLowerCase(),
      password: document.getElementById("password").value
    };

    const response = await fetch("/api/login", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify(data)
    });

    const result = await response.json();

    if (response.ok) {
      loginModal.classList.remove("d-none");
      setTimeout(() => window.location.href = "/", 1500);
    } else {
      loginErrorMsg.textContent = result.error || "Login failed. Try again.";
    }

    submitBtn.disabled = false;
    submitBtn.textContent = originalBtnText;
  });
}
