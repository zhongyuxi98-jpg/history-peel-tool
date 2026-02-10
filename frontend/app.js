// =====================
// Load mission question
// =====================
async function loadMission() {
  const params = new URLSearchParams(window.location.search);
  const missionId = params.get("mission");

  if (!missionId) {
    document.body.innerHTML = "No mission selected.";
    return;
  }

  const res = await fetch("../data/missions.json");
  const missions = await res.json();

  const mission = missions[missionId];

  if (!mission) {
    document.body.innerHTML = "Mission not found.";
    return;
  }

  const questionEl = document.getElementById("question");
  if (questionEl) {
    questionEl.innerText = mission.question;
  }
}

// =====================
// Submit essay to API
// =====================
async function submitEssay() {
  const textarea = document.getElementById("essayInput");
  const essayText = textarea.value.trim();

  if (!essayText) {
    alert("Please write an essay before submitting.");
    return;
  }

  try {
    const apiBase = window.location.hostname === 'localhost' && window.location.port === '8000'
      ? 'http://localhost:5501' : '';
    const response = await fetch(`${apiBase}/api/review`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ essay: essayText })
    });

    const data = await response.json();

    console.log("AI Review JSON:", data);

    // Phase 2 渲染入口（下一步实现）
    renderReview(data);

  } catch (error) {
    console.error("Error submitting essay:", error);
    alert("Failed to submit essay.");
  }
}

// =====================
// Placeholder renderer
// =====================
function renderReview(data) {
  const panel = document.getElementById("academic-review-panel");
  if (!panel) return;

  panel.innerHTML = `
    <pre style="white-space:pre-wrap;">${JSON.stringify(data, null, 2)}</pre>
  `;
}

// =====================
// Init
// =====================
document.addEventListener("DOMContentLoaded", () => {
  loadMission();

  const submitBtn = document.getElementById("submitBtn");
  if (submitBtn) {
    submitBtn.addEventListener("click", submitEssay);
  }
});
