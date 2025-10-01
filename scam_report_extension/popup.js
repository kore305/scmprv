document.getElementById("scamForm").addEventListener("submit", async (e) => {
  e.preventDefault();

  const data = {
    initiative_type: document.getElementById("initiative_type").value,
    reference: document.getElementById("reference").value,
    description: document.getElementById("description").value,
    contact: document.getElementById("contact").value,
    platform: Array.from(document.querySelectorAll("input[name=platform]:checked"))
                   .map(cb => cb.value)
  };

  const resultEl = document.getElementById("resultMessage");

  try {
    const response = await fetch("https://safecheck.up.railway.app/api/report-scam/", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(data)
    });

    if (response.ok) {
      resultEl.textContent = "✅ Report submitted successfully!";
      resultEl.className = "mt-4 text-green-600 font-semibold";
      document.getElementById("scamForm").reset();
    } else {
      resultEl.textContent = "❌ Error submitting report. Please try again.";
      resultEl.className = "mt-4 text-red-600 font-semibold";
    }
  } catch (err) {
    resultEl.textContent = "⚠️ Network error. Check your internet.";
    resultEl.className = "mt-4 text-yellow-600 font-semibold";
  }
});
