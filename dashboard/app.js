const API_URL = 'http://127.0.0.1:5000/api/v1/network/status';

let previousFusionsCount = 0;
let lastDataString = "";

async function fetchNetworkStatus() {
    try {
        const response = await fetch(API_URL);
        const data = await response.json();
        
        // Prevent DOM twitching by only rendering when data changes
        const currentDataString = JSON.stringify(data);
        if (currentDataString !== lastDataString) {
            updateDashboard(data);
            lastDataString = currentDataString;
        }
    } catch (error) {
        console.error("Error fetching network status:", error);
    }
}

function updateDashboard(data) {
    // Update metrics
    document.getElementById('waiting-count').textContent = data.waiting_nodes;
    document.getElementById('active-regions-count').textContent = data.active_regions.length;
    
    // Check for new fusions to trigger animation
    const currentFusionsCount = data.recent_fusions ? data.recent_fusions.length : 0;
    if (currentFusionsCount > previousFusionsCount) {
        triggerFusionAnimation();
        previousFusionsCount = currentFusionsCount;
    }
    
    if (data.recent_fusions) {
        document.getElementById('total-fusions-count').textContent = data.recent_fusions.length;
    }

    // Render Waiting Nodes
    const waitingList = document.getElementById('waiting-nodes-list');
    if (data.nodes.length === 0) {
        waitingList.innerHTML = '<div class="empty-state">No nodes waiting for fusion</div>';
    } else {
        waitingList.innerHTML = data.nodes.map(node => `
            <div class="node-card">
                <div class="node-header">
                    <span class="node-id">${node.id}</span>
                    <span class="node-region">${node.region}</span>
                </div>
                <div class="node-hash">Hash: ${node.hash_preview}...</div>
            </div>
        `).join('');
    }

    // Render Fusion History
    const historyList = document.getElementById('fusion-history-list');
    if (!data.recent_fusions || data.recent_fusions.length === 0) {
        historyList.innerHTML = '<div class="empty-state">Awaiting first successful fusion...</div>';
    } else {
        historyList.innerHTML = data.recent_fusions.map((fusion, index) => {
            const timeString = new Date(fusion.timestamp * 1000).toLocaleTimeString();
            // Add 'new' class to the most recent one to trigger highlight
            const isNew = index === 0 ? 'new' : '';
            return `
                <div class="fusion-card ${isNew}">
                    <div class="fusion-time">${timeString}</div>
                    <div class="fusion-nodes">
                        <span>${fusion.node_1.split('_')[0]}_${fusion.node_1.split('_')[1]}</span>
                        <span class="fusion-arrow">⤫</span>
                        <span>${fusion.node_2.split('_')[0]}_${fusion.node_2.split('_')[1]}</span>
                    </div>
                    <div class="master-key">Proof: ${fusion.proof_preview}...</div>
                </div>
            `;
        }).join('');
    }
}

function triggerFusionAnimation() {
    const flash = document.getElementById('fusion-flash');
    flash.classList.remove('active');
    // Trigger reflow to restart animation
    void flash.offsetWidth;
    flash.classList.add('active');
}

// Start polling every second
setInterval(fetchNetworkStatus, 1000);
fetchNetworkStatus(); // Initial fetch
