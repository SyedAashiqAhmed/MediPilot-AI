const form = document.getElementById("patientForm");
const output = document.getElementById("jsonOutput");

form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const patientData = {
        patient_id: document.getElementById("patient_id").value.trim(),
        symptoms: document.getElementById("symptoms").value.trim(),
        vitals: {
            bp: document.getElementById("bp").value.trim(),
            hr: document.getElementById("hr").value.trim(),
            spo2: document.getElementById("spo2").value.trim()
        },
        lab_results: {
            ecg: document.getElementById("ecg").value.trim(),
            troponin: document.getElementById("troponin").value.trim(),
            cholesterol: document.getElementById("cholesterol").value.trim()
        }
    };

    // Display JSON on page
    output.textContent = JSON.stringify(patientData, null, 4);

    try {
        const response = await fetch("/submit_patient", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(patientData)
        });

        if (!response.ok) {
            const text = await response.text();
            console.error("Server returned HTML:", text);
            alert("Error submitting data. Check console.");
            return;
        }

        const resData = await response.json();
        alert(resData.message);

        form.reset();
    } catch (error) {
        console.error(error);
        alert("Error submitting data: " + error);
    }
});
