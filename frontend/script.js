function convertMarkdownToHTML(markdown) {
  return markdown
    .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
    .replace(/\*(.*?)\*/g, "<em>$1</em>");
}

function typeText(element, text, speed = 30) {
  element.innerHTML = '';
  let index = 0;
  function type() {
    if (index < text.length) {
      element.innerHTML += text.charAt(index);
      index++;
      setTimeout(type, speed);
    }
  }
  type();
}

function showSection(sectionId) {
  document.querySelectorAll('.section').forEach(section => {
    section.classList.remove('active');
  });
  document.querySelectorAll('.tag').forEach(tag => {
    tag.classList.remove('active');
  });
  document.getElementById(sectionId).classList.add('active');
  document.querySelector(`button[onclick="showSection('${sectionId}')"]`).classList.add('active');
}

function parseMindMapToVisData(mindMapText) {
  const nodes = [];
  const edges = [];
  const lines = mindMapText.split('\n');
  let nodeId = 1;
  const nodeMap = {};

  lines.forEach(line => {
    const indentLevel = (line.match(/^\s*-/) ? line.match(/^\s*/)[0].length / 2 : 0);
    const content = line.replace(/^\s*-+\s*/, '').trim();
    if (!content) return;

    const node = { id: nodeId, label: content, level: indentLevel };
    nodes.push(node);
    nodeMap[indentLevel] = nodeId;

    if (indentLevel > 0) {
      const parentLevel = indentLevel - 1;
      if (nodeMap[parentLevel]) {
        edges.push({ from: nodeMap[parentLevel], to: nodeId });
      }
    }

    nodeId++;
  });

  return { nodes: new vis.DataSet(nodes), edges: new vis.DataSet(edges) };
}

function renderMindMap(mindMapText) {
  const container = document.getElementById('mindMapContainer');
  const data = parseMindMapToVisData(mindMapText);
  const options = {
    layout: {
      hierarchical: {
        direction: 'UD', // Up-Down direction
        sortMethod: 'directed',
        levelSeparation: 150, // Increase vertical spacing between levels
        nodeSpacing: 200, // Increase horizontal spacing between nodes
        treeSpacing: 300 // Increase spacing between different branches
      }
    },
    nodes: {
      shape: 'box',
      color: { background: '#1d1d1d', border: '#fff' },
      font: { color: '#fff', size: 14 },
      widthConstraint: { maximum: 200 } // Prevent nodes from being too wide
    },
    edges: {
      color: '#fff',
      smooth: { type: 'curvedCW', roundness: 0.2 }
    },
    physics: {
      enabled: false // Disable physics to maintain hierarchical layout
    },
    interaction: {
      dragNodes: true,
      zoomView: true,
      dragView: true
    }
  };
  const network = new vis.Network(container, data, options);

  // Fit the network to the container after rendering
  setTimeout(() => {
    network.fit();
  }, 500);
}

async function uploadPDF() {
  const fileInput = document.getElementById('pdfInput');
  const statusDiv = document.getElementById('status');
  const summaryText = document.getElementById('summaryText');
  const snippetText = document.getElementById('snippetText');
  const mindMapText = document.getElementById('mindMapText');
  const mcqText = document.getElementById('mcqText');
  const studyPlanText = document.getElementById('studyPlanText');

  if (fileInput.files.length === 0) {
    alert("Please select a PDF file.");
    return;
  }

  const file = fileInput.files[0];
  const formData = new FormData();
  formData.append("file", file);

  statusDiv.innerHTML = "<p class='loading'>⏳ Uploading and processing...</p>";
  typeText(summaryText, "Typing summary...");
  typeText(snippetText, "Typing snippet...");
  typeText(mindMapText, "Generating mind map...");
  typeText(mcqText, "Generating MCQs...");
  typeText(studyPlanText, "Preparing study plan...");

  try {
    const [summaryRes, mindMapRes, mcqRes, studyPlanRes] = await Promise.all([
      fetch("http://127.0.0.1:8000/upload-pdf/", { method: "POST", body: formData }),
      fetch("http://127.0.0.1:8000/generate-mindmap/", { method: "POST", body: formData }),
      fetch("http://127.0.0.1:8000/generate-mcqs/", { method: "POST", body: formData }),
      fetch("http://127.0.0.1:8000/generate-study-plan/", { method: "POST", body: formData })
    ]);

    if (!summaryRes.ok || !mindMapRes.ok || !mcqRes.ok || !studyPlanRes.ok) {
      throw new Error("One of the API calls failed.");
    }

    const summaryResult = await summaryRes.json();
    const mindMapResult = await mindMapRes.json();
    const mcqResult = await mcqRes.json();
    const studyPlanResult = await studyPlanRes.json();

    // Render Summary
    const summaryList = summaryResult.summary
      .split("* ")
      .filter(line => line.trim() !== "")
      .map(line => {
        const cleanLine = line.replace(/^\*+/, "").trim();
        return `<li>${convertMarkdownToHTML(cleanLine)}</li>`;
      }).join("");
    summaryText.innerHTML = `<ul>${summaryList}</ul>`;

    // Render Snippet
    const snippetList = summaryResult.text_snippet
      .split(/\. +/)
      .filter(sentence => sentence.trim() !== "")
      .map(sentence => `<li>${sentence.trim()}.</li>`)
      .join("");
    snippetText.innerHTML = `<ul>${snippetList}</ul>`;

    // Render Mind Map
    mindMapText.innerText = mindMapResult.mind_map;
    renderMindMap(mindMapResult.mind_map);

    // Render MCQs
    const mcqs = mcqResult.mcqs;
    mcqText.innerHTML = "";
    mcqs.forEach((mcq, i) => {
      if (mcq.error) {
        mcqText.innerHTML = `<p style="color:red;">${mcq.error}</p>`;
        return;
      }

      const questionDiv = document.createElement("div");
      questionDiv.className = "mcq-block";
      questionDiv.innerHTML = `<p><strong>Q${i + 1}:</strong> ${mcq.question}</p>`;

      for (const [key, value] of Object.entries(mcq.options)) {
        const button = document.createElement("button");
        button.innerText = `${key}. ${value}`;
        button.onclick = () => {
          const allButtons = questionDiv.querySelectorAll("button");
          allButtons.forEach(btn => btn.disabled = true);

          if (key === mcq.answer) {
            button.classList.add("correct");
          } else {
            button.classList.add("incorrect");
            allButtons.forEach(btn => {
              if (btn.innerText.startsWith(mcq.answer + ".")) {
                btn.classList.add("correct");
              }
            });
          }

          const explanationDiv = document.createElement("div");
          explanationDiv.innerHTML = `<em>${mcq.explanation}</em>`;
          explanationDiv.style.marginTop = "10px";
          questionDiv.appendChild(explanationDiv);
        };
        questionDiv.appendChild(button);
        questionDiv.appendChild(document.createElement("br"));
      }

      mcqText.appendChild(questionDiv);
    });

    // Render Study Plan
    studyPlanText.innerText = studyPlanResult.study_plan.replace(/\*+/g, '').trim();

    statusDiv.innerHTML = "<p style='color: green;'>✅ All done!</p>";
    showSection('summary'); // Default to summary
  } catch (error) {
    console.error("Upload failed:", error);
    statusDiv.innerHTML = "<p style='color: red;'>❌ Failed to process PDF.</p>";
  }
}

function copyText(elementId) {
  const element = document.getElementById(elementId);
  if (!element) {
    alert("Element not found!");
    return;
  }
  const temp = document.createElement("textarea");
  temp.value = element.innerText;
  document.body.appendChild(temp);
  temp.select();
  document.execCommand("copy");
  document.body.removeChild(temp);
  alert("Copied to clipboard!");
}

function downloadText(elementId, filename) {
  const element = document.getElementById(elementId);
  if (!element) {
    alert("Element not found!");
    return;
  }
  const text = element.innerText;
  const blob = new Blob([text], { type: "text/plain" });
  const link = document.createElement("a");
  link.download = filename;
  link.href = window.URL.createObjectURL(blob);
  link.click();
}