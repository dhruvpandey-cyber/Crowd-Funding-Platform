const API = "/api";

function getToken() {
    return localStorage.getItem("cf_token") || "";
}

function authHeaders() {
    const token = getToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
}

async function api(path, options = {}) {
    const response = await fetch(`${API}${path}`, {
        ...options,
        headers: {
            "Content-Type": "application/json",
            ...authHeaders(),
            ...(options.headers || {}),
        },
    });

    let data = {};
    try {
        data = await response.json();
    } catch (error) {
        data = {};
    }

    if (!response.ok) {
        const msg = data.detail || JSON.stringify(data) || "Request failed";
        throw new Error(msg);
    }
    return data;
}

async function apiForm(path, formData, options = {}) {
    const response = await fetch(`${API}${path}`, {
        method: options.method || "POST",
        headers: {
            ...authHeaders(),
            ...(options.headers || {}),
        },
        body: formData,
    });

    let data = {};
    try {
        data = await response.json();
    } catch (error) {
        data = {};
    }

    if (!response.ok) {
        const msg = data.detail || JSON.stringify(data) || "Request failed";
        throw new Error(msg);
    }
    return data;
}

function setFlash(id, message, isError = false) {
    const el = document.getElementById(id);
    if (!el) return;
    el.classList.add("show");
    el.style.background = isError ? "rgba(239, 108, 50, 0.15)" : "rgba(15, 156, 144, 0.12)";
    el.style.borderColor = isError ? "rgba(239, 108, 50, 0.3)" : "rgba(15, 156, 144, 0.3)";
    el.textContent = message;
}

function formatCurrency(value) {
    const num = Number(value || 0);
    return `$${num.toFixed(2)}`;
}

function toArray(data) {
    if (Array.isArray(data)) return data;
    if (Array.isArray(data?.results)) return data.results;
    return [];
}

function getCampaignIdFromPath() {
    const match = window.location.pathname.match(/\/campaigns\/(\d+)\/?$/);
    return match ? Number(match[1]) : null;
}

function setActiveNav() {
    const current = window.location.pathname;
    document.querySelectorAll(".nav-links a").forEach((link) => {
        const href = link.getAttribute("href");
        if (!href || href === "/auth/") return;
        if ((href === "/" && current === "/") || (href !== "/" && current.startsWith(href))) {
            link.classList.add("is-active");
        }
    });
}

function wireAuthLink() {
    const link = document.getElementById("auth-link");
    if (!link) return;
    if (getToken()) {
        link.textContent = "Logout";
        link.href = "#";
        link.addEventListener("click", (e) => {
            e.preventDefault();
            localStorage.removeItem("cf_token");
            window.location.href = "/auth/";
        });
    }
}

async function initAuthPage() {
    const loginForm = document.getElementById("login-form");
    const registerForm = document.getElementById("register-form");

    loginForm?.addEventListener("submit", async (e) => {
        e.preventDefault();
        const formData = new FormData(loginForm);
        try {
            const data = await api("/auth/token/", {
                method: "POST",
                body: JSON.stringify({
                    username: formData.get("username"),
                    password: formData.get("password"),
                }),
            });
            localStorage.setItem("cf_token", data.access);
            setFlash("auth-message", "Login successful. Redirecting...");
            setTimeout(() => {
                window.location.href = "/dashboard/";
            }, 700);
        } catch (error) {
            setFlash("auth-message", error.message, true);
        }
    });

    registerForm?.addEventListener("submit", async (e) => {
        e.preventDefault();
        const formData = new FormData(registerForm);
        try {
            await api("/auth/register/", {
                method: "POST",
                body: JSON.stringify({
                    username: formData.get("username"),
                    email: formData.get("email"),
                    first_name: formData.get("first_name"),
                    last_name: formData.get("last_name"),
                    role: formData.get("role"),
                    phone_number: formData.get("phone_number"),
                    password: formData.get("password"),
                }),
            });
            setFlash("auth-message", "Registration successful. Please login.");
            registerForm.reset();
        } catch (error) {
            setFlash("auth-message", error.message, true);
        }
    });
}

async function initCampaignsPage() {
    const grid = document.getElementById("campaign-grid");
    const searchInput = document.getElementById("campaign-search");
    const statusSelect = document.getElementById("campaign-status");
    if (!grid) return;

    const renderCampaigns = (list) => {
        if (!list.length) {
            grid.innerHTML = "<article class='card'><h3>No campaigns found</h3><p>Try changing search or filters.</p></article>";
            return;
        }

        grid.innerHTML = list
            .map(
                (c) => `
                <article class="card">
                    ${c.hero_media_url ? `<img class="campaign-cover" src="${c.hero_media_url}" alt="${c.title}" />` : ""}
                    <h3>${c.title}</h3>
                    <p>${c.short_description}</p>
                    <p><strong>Goal:</strong> ${formatCurrency(c.goal_amount)}</p>
                    <p><strong>Raised:</strong> ${formatCurrency(c.total_raised)}</p>
                    <div class="progress">
                        <p><strong>Progress:</strong> ${c.progress_percent}%</p>
                        <div class="progress-track"><span style="width:${Math.min(100, Number(c.progress_percent || 0))}%"></span></div>
                    </div>
                    <p><strong>Status:</strong> ${c.status}</p>
                    <a class="btn btn-ghost" href="/campaigns/${c.id}/">View Details</a>
                </article>
            `
            )
            .join("");
    };

    try {
        const campaignsRaw = await api("/campaigns/");
        const campaigns = toArray(campaignsRaw);
        if (!campaigns.length) {
            grid.innerHTML = "<article class='card'><h3>No campaigns yet</h3><p>Be the first to launch one.</p></article>";
            return;
        }

        const applyFilters = () => {
            const text = (searchInput?.value || "").toLowerCase();
            const selectedStatus = statusSelect?.value || "ALL";
            const filtered = campaigns.filter((c) => {
                const matchesText =
                    c.title.toLowerCase().includes(text) ||
                    (c.short_description || "").toLowerCase().includes(text);
                const matchesStatus = selectedStatus === "ALL" || c.status === selectedStatus;
                return matchesText && matchesStatus;
            });
            renderCampaigns(filtered);
        };

        searchInput?.addEventListener("input", applyFilters);
        statusSelect?.addEventListener("change", applyFilters);
        renderCampaigns(campaigns);
    } catch (error) {
        grid.innerHTML = `<article class="card"><h3>Error</h3><p>${error.message}</p></article>`;
    }
}

async function initCampaignDetailPage() {
    const campaignId = getCampaignIdFromPath();
    const detailCard = document.getElementById("campaign-detail-card");
    const pledgeForm = document.getElementById("pledge-form");

    if (!campaignId || !detailCard) {
        return;
    }

    try {
        const campaign = await api(`/campaigns/${campaignId}/`);
        detailCard.innerHTML = `
            <h2>${campaign.title}</h2>
            <div class="media-grid">
                ${
                    campaign.media?.length
                        ? campaign.media
                              .map((m) => {
                                  const src = m.file || m.external_url;
                                  if (!src) return "";
                                  return `<img class="campaign-cover" src="${src}" alt="${campaign.title}" />`;
                              })
                              .join("")
                        : ""
                }
            </div>
            <p>${campaign.short_description}</p>
            <p>${campaign.story}</p>
            <p><strong>Goal:</strong> ${formatCurrency(campaign.goal_amount)}</p>
            <p><strong>Raised:</strong> ${formatCurrency(campaign.total_raised)}</p>
            <p><strong>Progress:</strong> ${campaign.progress_percent}%</p>
            <p><strong>Status:</strong> ${campaign.status}</p>
            <p><strong>Min pledge:</strong> ${formatCurrency(campaign.min_pledge_amount)}</p>
            <p><strong>Deadline:</strong> ${new Date(campaign.deadline).toLocaleString()}</p>
            <hr />
            <h3>Reward Tiers</h3>
            <div>
                ${
                    campaign.reward_tiers?.length
                        ? campaign.reward_tiers
                              .map(
                                  (r) => `
                        <p><strong>ID ${r.id}:</strong> ${r.title} - ${formatCurrency(r.amount)} (${r.claimed_count} claimed)</p>
                    `
                              )
                              .join("")
                        : "<p>No rewards added yet.</p>"
                }
            </div>
        `;
    } catch (error) {
        detailCard.innerHTML = `<p>${error.message}</p>`;
    }

    pledgeForm?.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (!getToken()) {
            setFlash("pledge-message", "Please login to pledge.", true);
            return;
        }

        const formData = new FormData(pledgeForm);
        const amount = formData.get("amount");
        const rewardTier = formData.get("reward_tier");
        const gateway = formData.get("gateway") || "sandbox";

        try {
            const pledge = await api("/pledges/", {
                method: "POST",
                body: JSON.stringify({
                    campaign: campaignId,
                    amount,
                    ...(rewardTier ? { reward_tier: rewardTier } : {}),
                }),
            });

            await api("/payments/sandbox/checkout/", {
                method: "POST",
                body: JSON.stringify({
                    pledge_id: pledge.id,
                    gateway,
                }),
            });

            setFlash("pledge-message", "Pledge and sandbox payment completed successfully.");
            pledgeForm.reset();
        } catch (error) {
            setFlash("pledge-message", error.message, true);
        }
    });
}

async function initCreateCampaignPage() {
    const form = document.getElementById("create-campaign-form");
    if (!form) return;

    if (!getToken()) {
        setFlash("create-message", "Login required to create a campaign.", true);
        return;
    }

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const formData = new FormData(form);
        const deadlineInput = formData.get("deadline");
        const heroImage = formData.get("hero_image");

        try {
            const campaign = await api("/campaigns/", {
                method: "POST",
                body: JSON.stringify({
                    title: formData.get("title"),
                    short_description: formData.get("short_description"),
                    story: formData.get("story"),
                    goal_amount: formData.get("goal_amount"),
                    min_pledge_amount: formData.get("min_pledge_amount"),
                    deadline: new Date(deadlineInput).toISOString(),
                }),
            });

            if (heroImage && heroImage.size > 0) {
                const mediaData = new FormData();
                mediaData.append("campaign", campaign.id);
                mediaData.append("media_type", "IMAGE");
                mediaData.append("file", heroImage);
                await apiForm("/campaigns/media/", mediaData, { method: "POST" });
            }

            setFlash("create-message", "Campaign created successfully with media upload.");
            form.reset();
        } catch (error) {
            setFlash("create-message", error.message, true);
        }
    });
}

async function initAnalyticsPage() {
    const campaignsMetric = document.getElementById("metric-campaigns");
    const pledgesMetric = document.getElementById("metric-pledges");
    const raisedMetric = document.getElementById("metric-raised");
    const goalsChart = document.getElementById("goals-chart");
    const pledgeStatusChart = document.getElementById("pledge-status-chart");

    if (!campaignsMetric || !pledgesMetric || !raisedMetric || !goalsChart || !pledgeStatusChart) {
        return;
    }

    try {
        const campaigns = await api("/campaigns/");
        const pledges = getToken() ? await api("/pledges/") : [];

        const totalRaised = campaigns.reduce((sum, c) => sum + Number(c.total_raised || 0), 0);
        campaignsMetric.textContent = campaigns.length;
        pledgesMetric.textContent = pledges.length;
        raisedMetric.textContent = formatCurrency(totalRaised);

        if (typeof Chart !== "undefined") {
            new Chart(goalsChart, {
                type: "bar",
                data: {
                    labels: campaigns.slice(0, 8).map((c) => c.title.slice(0, 16)),
                    datasets: [
                        {
                            label: "Goal",
                            data: campaigns.slice(0, 8).map((c) => Number(c.goal_amount || 0)),
                            backgroundColor: "rgba(239,108,50,0.72)",
                        },
                        {
                            label: "Raised",
                            data: campaigns.slice(0, 8).map((c) => Number(c.total_raised || 0)),
                            backgroundColor: "rgba(15,156,144,0.72)",
                        },
                    ],
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                },
            });

            const statusCounts = pledges.reduce((acc, p) => {
                acc[p.status] = (acc[p.status] || 0) + 1;
                return acc;
            }, {});

            new Chart(pledgeStatusChart, {
                type: "doughnut",
                data: {
                    labels: Object.keys(statusCounts),
                    datasets: [
                        {
                            data: Object.values(statusCounts),
                            backgroundColor: ["#ef6c32", "#0f9c90", "#2f6fed", "#f4b400", "#cf4a63"],
                        },
                    ],
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                },
            });
        }
    } catch (error) {
        campaignsMetric.textContent = error.message;
    }
}

async function initDashboardPage() {
    const profileBox = document.getElementById("profile-box");
    const pledgesBox = document.getElementById("pledges-box");
    const notificationsBox = document.getElementById("notifications-box");
    const creatorCampaignsBox = document.getElementById("creator-campaigns-box");
    const chartBox = document.getElementById("chart-box");
    const incomingBox = document.getElementById("incoming-box");
    const metricCampaignCount = document.getElementById("metric-campaign-count");
    const metricReceived = document.getElementById("metric-received");
    const metricPledges = document.getElementById("metric-pledges");
    const metricActive = document.getElementById("metric-active-campaigns");

    if (!getToken()) {
        if (profileBox) profileBox.innerHTML = "Login required. <a href='/auth/'>Go to auth page</a>.";
        if (pledgesBox) pledgesBox.textContent = "-";
        if (notificationsBox) notificationsBox.textContent = "-";
        if (creatorCampaignsBox) creatorCampaignsBox.textContent = "-";
        if (chartBox) chartBox.textContent = "-";
        if (incomingBox) incomingBox.textContent = "-";
        if (metricCampaignCount) metricCampaignCount.textContent = "-";
        if (metricReceived) metricReceived.textContent = "-";
        if (metricPledges) metricPledges.textContent = "-";
        if (metricActive) metricActive.textContent = "-";
        return;
    }

    if (profileBox) profileBox.textContent = "Loading profile...";
    if (pledgesBox) pledgesBox.textContent = "Loading pledges...";
    if (notificationsBox) notificationsBox.textContent = "Loading notifications...";
    if (creatorCampaignsBox) creatorCampaignsBox.textContent = "Loading creator controls...";
    if (chartBox) chartBox.textContent = "Loading chart...";
    if (incomingBox) incomingBox.textContent = "Loading incoming contributions...";
    if (metricCampaignCount) metricCampaignCount.textContent = "...";
    if (metricReceived) metricReceived.textContent = "...";
    if (metricPledges) metricPledges.textContent = "...";
    if (metricActive) metricActive.textContent = "...";

    let normalizedRole = "";

    try {
        const profile = await api("/auth/profile/");
        normalizedRole = (profile?.role || "").toString().trim().toUpperCase();
        if (profileBox) {
            profileBox.innerHTML = `
                <p><strong>${profile.username}</strong></p>
                <p>${profile.email || "No email"}</p>
                <p>Role: ${profile.role}</p>
            `;
        }
    } catch (error) {
        if (profileBox) profileBox.textContent = error.message;
    }

    let pledgesData = [];
    let creatorStats = null;
    try {
        const pledges = await api("/pledges/");
        pledgesData = toArray(pledges);
        if (pledgesBox) {
            pledgesBox.innerHTML = pledgesData.length
                ? pledgesData
                      .slice(0, 5)
                      .map((p) => `<p>#${p.id} - ${formatCurrency(p.amount)} (${p.status})</p>`)
                      .join("")
                : "<p>No pledges yet.</p>";
        }
    } catch (error) {
        if (pledgesBox) pledgesBox.textContent = error.message;
    }

    try {
        const notes = await api("/notifications/");
        const notesList = toArray(notes);
        if (notificationsBox) {
            notificationsBox.innerHTML = notesList.length
                ? notesList.slice(0, 5).map((n) => `<p>${n.title}</p>`).join("")
                : "<p>No notifications.</p>";
        }
    } catch (error) {
        if (notificationsBox) notificationsBox.textContent = error.message;
    }

    if (normalizedRole === "CREATOR" || normalizedRole === "ADMIN") {
        try {
            creatorStats = await api("/campaigns/creator-stats/");
            if (incomingBox) {
                incomingBox.innerHTML = creatorStats.recent_pledges?.length
                    ? creatorStats.recent_pledges
                          .slice(0, 6)
                          .map(
                              (p) => `<p><strong>${p.backer_name}</strong> pledged ${formatCurrency(p.amount)} to ${p.campaign_title} (${p.status})</p>`
                          )
                          .join("")
                    : "<p>No incoming contributions yet.</p>";
            }
            if (metricCampaignCount) metricCampaignCount.textContent = `${creatorStats.campaign_count || 0}`;
            if (metricReceived) metricReceived.textContent = formatCurrency(creatorStats.received_total || 0);
            if (metricPledges) metricPledges.textContent = `${creatorStats.all_pledges_count || 0}`;
        } catch (error) {
            if (incomingBox) incomingBox.textContent = error.message;
        }
    } else if (incomingBox) {
        incomingBox.innerHTML = "<p>Incoming contributions are shown for creator accounts.</p>";
    }

    if (chartBox) {
        try {
            let total = pledgesData.reduce((sum, p) => sum + Number(p.amount || 0), 0);
            let captured = pledgesData.filter((p) => p.status === "CAPTURED").length;
            let totalPledges = pledgesData.length;

            if (creatorStats) {
                total = Number(creatorStats.received_total || 0);
                captured = Number(creatorStats.received_pledges_count || 0);
                totalPledges = Number(creatorStats.all_pledges_count || 0);
            }

            const bars = [
                {
                    label: creatorStats ? "Total received" : "Total pledged",
                    value: Math.min(100, total / 10),
                    text: formatCurrency(total),
                },
                {
                    label: creatorStats ? "Received pledges" : "Captured pledges",
                    value: Math.min(100, captured * 15),
                    text: `${captured}`,
                },
                {
                    label: creatorStats ? "All incoming pledges" : "Total pledges",
                    value: Math.min(100, totalPledges * 10),
                    text: `${totalPledges}`,
                },
            ];
            chartBox.innerHTML = bars
                .map(
                    (b) => `
                    <div class="bar-row">
                        <p><strong>${b.label}</strong>: ${b.text}</p>
                        <div class="bar-track"><span style="width:${b.value}%"></span></div>
                    </div>
                `
                )
                .join("");
        } catch (error) {
            chartBox.textContent = "Unable to render chart right now.";
        }
    }

    if (!creatorCampaignsBox) {
        return;
    }

    if (normalizedRole !== "CREATOR" && normalizedRole !== "ADMIN") {
        creatorCampaignsBox.innerHTML = `<p>Creator controls are available for CREATOR role. Current role: ${normalizedRole || "UNKNOWN"}.</p>`;
        return;
    }

    try {
        const campaignsResponse = await api("/campaigns/mine/");
        const campaigns = toArray(campaignsResponse);
        if (metricActive) {
            metricActive.textContent = `${campaigns.filter((c) => c.status === "ACTIVE").length}`;
        }
        creatorCampaignsBox.innerHTML = campaigns.length
            ? campaigns
                  .map(
                      (c) => `
                    <div class="creator-item">
                        <p><strong>${c.title}</strong> (${c.status})</p>
                        <div class="split">
                            <select data-status-id="${c.id}">
                                <option value="DRAFT" ${c.status === "DRAFT" ? "selected" : ""}>DRAFT</option>
                                <option value="PENDING_REVIEW" ${c.status === "PENDING_REVIEW" ? "selected" : ""}>PENDING_REVIEW</option>
                                <option value="ACTIVE" ${c.status === "ACTIVE" ? "selected" : ""}>ACTIVE</option>
                                <option value="CANCELLED" ${c.status === "CANCELLED" ? "selected" : ""}>CANCELLED</option>
                            </select>
                            <button class="btn btn-ghost" data-status-btn="${c.id}">Update</button>
                        </div>
                    </div>
                `
                  )
                  .join("")
            : "<p>You have not created campaigns yet.</p>";

        document.querySelectorAll("[data-status-btn]").forEach((button) => {
            button.addEventListener("click", async () => {
                const id = button.getAttribute("data-status-btn");
                const select = document.querySelector(`[data-status-id='${id}']`);
                const selectedStatus = select?.value;
                try {
                    await api(`/campaigns/${id}/set_status/`, {
                        method: "POST",
                        body: JSON.stringify({ status: selectedStatus }),
                    });
                    button.textContent = "Updated";
                    setTimeout(() => {
                        button.textContent = "Update";
                    }, 1200);
                } catch (error) {
                    button.textContent = "Error";
                }
            });
        });
    } catch (error) {
        creatorCampaignsBox.textContent = error.message;
    }
}

async function initAdminPanelPage() {
    const box = document.getElementById("admin-reports-box");
    if (!box) return;
    if (!getToken()) {
        box.innerHTML = "<p>Login as admin to access moderation panel.</p>";
        return;
    }

    try {
        const reports = await api("/moderation/reports/");
        box.innerHTML = reports.length
            ? reports
                  .map(
                      (r) => `
                    <div class="creator-item">
                        <p><strong>Report #${r.id}</strong> on campaign ${r.campaign}</p>
                        <p>Reason: ${r.reason}</p>
                        <p>Current status: ${r.status}</p>
                        <div class="split">
                            <select data-report-id="${r.id}">
                                <option value="OPEN">OPEN</option>
                                <option value="UNDER_REVIEW">UNDER_REVIEW</option>
                                <option value="RESOLVED">RESOLVED</option>
                                <option value="REJECTED">REJECTED</option>
                            </select>
                            <button class="btn btn-ghost" data-report-btn="${r.id}">Save</button>
                        </div>
                    </div>
                `
                  )
                  .join("")
            : "<p>No reports found.</p>";

        document.querySelectorAll("[data-report-btn]").forEach((button) => {
            button.addEventListener("click", async () => {
                const id = button.getAttribute("data-report-btn");
                const select = document.querySelector(`[data-report-id='${id}']`);
                try {
                    await api(`/moderation/reports/${id}/`, {
                        method: "PATCH",
                        body: JSON.stringify({ status: select.value }),
                    });
                    setFlash("admin-message", `Report #${id} updated.`);
                } catch (error) {
                    setFlash("admin-message", error.message, true);
                }
            });
        });
    } catch (error) {
        box.innerHTML = `<p>${error.message}</p>`;
    }
}

(function init() {
    wireAuthLink();
    setActiveNav();
    const page = document.body.dataset.page;

    if (page === "auth") initAuthPage();
    if (page === "campaigns") initCampaignsPage();
    if (page === "campaign-detail") initCampaignDetailPage();
    if (page === "create-campaign") initCreateCampaignPage();
    if (page === "dashboard") initDashboardPage();
    if (page === "analytics") initAnalyticsPage();
    if (page === "admin-panel") initAdminPanelPage();
})();
