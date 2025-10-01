// Function to create context menu items
function createContextMenu() {
  chrome.contextMenus.create({
    id: "reportScam",
    title: "Report a Scam",
    contexts: ["all"],
    // Ensure to not create the item if it already exists
    // by removing it first (optional)
    // removeExistingMenuItems();
  });

  chrome.contextMenus.create({
    id: "scanUrl",
    title: "Scan this link with VirusTotal",
    contexts: ["link"],
    // Ensure to not create the item if it already exists
    // by removing it first (optional)
    // removeExistingMenuItems();
  });
}

// Call the function to create context menu items
createContextMenu();

// Optionally remove existing menu items before creating new ones
// function removeExistingMenuItems() {
//   chrome.contextMenus.remove("reportScam", () => {
//     chrome.contextMenus.remove("scanUrl", createContextMenu);
//   });
// }

// Event listener for the context menu click
chrome.contextMenus.onClicked.addListener((info, tab) => {
  console.log("Context menu item clicked", info);  // Log info to console
  if (info.menuItemId === "reportScam") {
    // Open the report scam page in a new tab
    chrome.tabs.create({ url: 'popup.html' });
  } else if (info.menuItemId === "scanUrl") {
    const url = info.linkUrl;
    console.log("URL to scan:", url);  // Log URL to console
    submitUrlToVirusTotal(url);
  }
});



// Function to submit URL to VirusTotal for scanning
// ... (previous code remains the same)

function submitUrlToVirusTotal(url) {
  console.log("Submitting URL for scan:", url);
  const apiKey = "8270c041b2bf7f04334f8fec1864bc07ca59dc32d27468a52df6aae9e7858a88"; // Ensure this is your actual, updated API key
  const apiUrl = `https://www.virustotal.com/api/v3/urls`;

  fetch(apiUrl, {
    method: "POST",
    headers: {
      "x-apikey": apiKey,
      "Content-Type": "application/x-www-form-urlencoded"
    },
    body: new URLSearchParams({
      url: url
    })
  })
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    console.log("Submission response:", data);
    if (data.data && data.data.id) {
      chrome.notifications.create({
        type: 'basic',
        iconUrl: 'icon.png',
        title: 'VirusTotal Scan',
        message: `URL submitted. Retrieving results shortly...`
      });
      // Wait a bit before fetching results
      setTimeout(() => getAnalysisResults(data.data.id, apiKey), 15000);
    } else {
      throw new Error('Unexpected response structure');
    }
  })
  .catch(error => {
    console.error("Error submitting URL:", error);
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icon.png',
      title: 'VirusTotal Scan',
      message: `Failed to submit URL. Error: ${error.message}`
    });
  });
}

function getAnalysisResults(analysisId, apiKey) {
  const apiUrl = `https://www.virustotal.com/api/v3/analyses/${analysisId}`;

  fetch(apiUrl, {
    method: "GET",
    headers: {
      "x-apikey": apiKey
    }
  })
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    return response.json();
  })
  .then(data => {
    console.log("Analysis results:", data);
    if (data.data && data.data.attributes && data.data.attributes.stats) {
      const stats = data.data.attributes.stats;
      const message = `Scan complete. Malicious: ${stats.malicious}, Suspicious: ${stats.suspicious}, Harmless: ${stats.harmless}`;
      chrome.notifications.create({
        type: 'basic',
        iconUrl: 'icon.png',
        title: 'VirusTotal Scan Results',
        message: message
      });
      // You might want to store the full results or open a new tab with detailed results
    } else {
      throw new Error('Unexpected results structure');
    }
  })
  .catch(error => {
    console.error("Error fetching analysis results:", error);
    chrome.notifications.create({
      type: 'basic',
      iconUrl: 'icon.png',
      title: 'VirusTotal Scan',
      message: `Failed to fetch results. Error: ${error.message}`
    });
  });
}

