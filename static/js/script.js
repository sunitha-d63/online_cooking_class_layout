document.addEventListener("DOMContentLoaded", () => {
  const signupForm = document.getElementById("signup-form");
  const signupErrorMsg = document.getElementById("signup-error-message");
  if (!signupForm || !signupErrorMsg) return;

signupForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  signupErrorMsg.textContent = "";

  const submitBtn = document.getElementById("signup-submit");
  if (!submitBtn) return;

  const originalText = submitBtn.textContent;
  submitBtn.disabled = true;

  const name = (document.getElementById("name")?.value || "").trim();
  const email = (document.getElementById("email")?.value || "").trim().toLowerCase();
  const mobile = document.getElementById("mobile")?.value.trim() || "";
  const password = document.getElementById("password")?.value || "";

  if (name.length < 3) {
    signupErrorMsg.textContent = "Name must be at least 3 characters.";
    submitBtn.disabled = false;
    return;
  }

  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailPattern.test(email)) {
    signupErrorMsg.textContent = "Please enter a valid email address.";
    submitBtn.disabled = false;
    return;
  }

  if (!/^\d{10}$/.test(mobile)) {
    signupErrorMsg.textContent = "Mobile number must be 10 digits.";
    submitBtn.disabled = false;
    return;
  }

  if (password.length < 6) {
    signupErrorMsg.textContent = "Password must be at least 6 characters.";
    submitBtn.disabled = false;
    return;
  }

  try {
    const res = await fetch("/api/signup", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name, email, mobile, password })
    });

    const result = await res.json();

    if (res.ok) {
      const modalEl = document.getElementById("successModal");
      if (modalEl) {
        new bootstrap.Modal(modalEl).show();
        setTimeout(() => (window.location.href = "/login"), 2000);
      } else {
        window.location.href = "/login";
      }
    } else {
      signupErrorMsg.textContent = result.error || "Signup failed!";
    }
  } catch (err) {
    console.error("Signup error:", err);
    signupErrorMsg.textContent = "Something went wrong. Please try again.";
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = originalText;
  }
});

});

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







