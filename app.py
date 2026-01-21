import streamlit as st
import streamlit.components.v1 as components

# --- ページ設定 ---
st.set_page_config(page_title="極方程式タッチシミュレータ Ultimate v5", layout="wide")

# --- メニュー完全消去CSS ---
hide_streamlit_style = """
            <style>
            [data-testid="stStatusWidget"] {visibility: hidden !important; display: none !important;}
            #MainMenu {visibility: hidden !important; display: none !important;}
            header {visibility: hidden !important; display: none !important;}
            footer {visibility: hidden !important; display: none !important;}
            [data-testid="stToolbar"] {visibility: hidden !important; display: none !important;}
            .stDeployButton {display: none !important;}
            [data-testid="stDecoration"] {visibility: hidden !important; display: none !important;}
            [data-testid="stAppDeployButton"] {display: none !important;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- タイトル ---
st.markdown("## 極方程式 タッチシミュレータ")
st.markdown("リストから方程式を選び、画面をタッチして操作してください。")

# --- 【修正1】リストボックスを小さくする ---
# col1, col2 = st.columns([1, 2]) とすることで、左側の狭いエリア(col1)にリストを置く
col1, col2 = st.columns([1, 3]) 

with col1:
    equation_map = {
        "r = 2": "circle_origin",
        "rcosθ = 1": "line_fixed",
        "r = 2cosθ": "circle_shifted",
        "rcos(θ - α) = 1": "line_alpha"
    }

    equation_choice = st.selectbox(
        "表示する極方程式:",
        list(equation_map.keys())
    )

mode = equation_map[equation_choice]

# --- HTML/JS埋め込みコード ---
html_template = """
<!DOCTYPE html>
<html>
<head>
<style>
    body { 
        font-family: 'Times New Roman', serif;
        user-select: none; -webkit-user-select: none; margin: 0; overflow: hidden; 
        background-color: white; touch-action: none;
    }
    #canvas-container { 
        position: relative; width: 100%; max-width: 600px; aspect-ratio: 1 / 1; 
        margin: 0 auto; cursor: grab;
    }
    #canvas-container:active { cursor: grabbing; }
    svg { width: 100%; height: 100%; display: block; } 
    
    .axis-label { font-size: 0.2px; fill: #666; font-style: italic; pointer-events: none; }
    .status-text { font-size: 0.28px; font-weight: bold; fill: #333; pointer-events: none; font-family: 'Arial'; }
    .graph-label { font-size: 0.25px; font-weight: bold; pointer-events: none; text-shadow: 1px 1px 0 #fff, -1px -1px 0 #fff, 1px -1px 0 #fff, -1px 1px 0 #fff;}
    
    /* 【修正2】数式表示のスタイル変更（サイズダウン） */
    #eq-display { 
        font-size: 0.25px; /* 0.4 -> 0.25 に縮小 */
        font-weight: bold; 
        fill: #333; 
        font-family: 'Times New Roman', serif; 
        font-style: italic; 
        pointer-events: none; 
        opacity: 0.8; 
    }
    
    .axis { stroke: #000; stroke-width: 0.02; pointer-events: none; }
    
    /* 動く要素 */
    #theta-arc { fill: none; stroke: orange; stroke-width: 0.05; stroke-linecap: round; pointer-events: none; }
    #sight-line { stroke: #999; stroke-width: 0.02; stroke-dasharray: 0.1, 0.1; pointer-events: none; }
    #radius-line { stroke-width: 0.07; stroke-linecap: round; pointer-events: none; }
    #trajectory { fill: none; stroke: black; stroke-width: 0.03; stroke-linecap: round; pointer-events: none; }
    
    /* αモード用の垂線 */
    #normal-line { stroke: blue; stroke-width: 0.03; stroke-dasharray: 0.1, 0.1; pointer-events: none; display: none;}
    #right-angle { fill: none; stroke: blue; stroke-width: 0.02; display: none;}

    #touch-layer { fill: transparent; cursor: grab; }
</style>
</head>
<body>

<div id="canvas-container">
    <svg id="main-svg" viewBox="-2.5 -2.5 5 5" preserveAspectRatio="xMidYMid meet">
        <defs>
            <marker id="arrow" markerWidth="4" markerHeight="4" refX="3" refY="2" orient="auto" markerUnits="strokeWidth">
                <path d="M0,0 L0,4 L4,2 z" fill="#000" />
            </marker>
        </defs>

        <line x1="-2.4" y1="0" x2="2.4" y2="0" class="axis" marker-end="url(#arrow)" />
        <line x1="0" y1="2.4" x2="0" y2="-2.4" class="axis" marker-end="url(#arrow)" />
        <text x="2.3" y="-0.1" class="axis-label">x</text>
        <text x="0.1" y="-2.3" class="axis-label">y</text>
        <text x="-0.2" y="0.2" class="axis-label">O</text>

        <text id="eq-display" x="-2.3" y="-2.0" text-anchor="start">__EQUATION_NAME__</text>

        <text id="info-angle" x="-2.3" y="-1.6" class="status-text">θ = 0</text>
        <text id="info-r" x="-2.3" y="-1.3" class="status-text">r = 0.00</text>

        <path id="trajectory" d="M 0,0" />
        
        <line id="normal-line" x1="0" y1="0" x2="0" y2="0" />
        <path id="right-angle" d="M0,0" />

        <line id="sight-line" x1="-5" y1="0" x2="5" y2="0" />
        <path id="theta-arc" d="M0,0" style="display:none"/>
        <line id="radius-line" x1="0" y1="0" x2="0" y2="0" stroke="red"/>
        <circle id="point-p" cx="0" cy="0" r="0.08" fill="red" pointer-events: none;/>
        
        <circle id="handle" cx="0" cy="0" r="0.2" fill="red" fill-opacity="0.3" stroke="none" pointer-events="none"/>

        <text id="label-theta" class="graph-label" fill="orange" x="0" y="0" style="display:none">θ</text>
        <text id="label-r" class="graph-label" fill="red" x="0" y="0">r</text>

        <rect id="touch-layer" x="-2.5" y="-2.5" width="5" height="5" />
    </svg>
</div>

<script>
    const currentMode = "__MODE_NAME__"; 

    const svg = document.getElementById('main-svg');
    const touchLayer = document.getElementById('touch-layer');
    const handle = document.getElementById('handle');
    const sightLine = document.getElementById('sight-line');
    const radiusLine = document.getElementById('radius-line');
    const pointP = document.getElementById('point-p');
    const thetaArc = document.getElementById('theta-arc');
    const trajectory = document.getElementById('trajectory');
    
    // αモード用要素
    const normalLine = document.getElementById('normal-line');
    const rightAngle = document.getElementById('right-angle');
    
    const infoAngle = document.getElementById('info-angle');
    const infoR = document.getElementById('info-r');
    const labelTheta = document.getElementById('label-theta');
    const labelR = document.getElementById('label-r');

    let isDragging = false;
    
    // マグネット吸着リスト
    const magnets = [
        {val: 0, label: "0"}, {val: Math.PI/6, label: "π/6"}, {val: Math.PI/4, label: "π/4"},
        {val: Math.PI/3, label: "π/3"}, {val: Math.PI/2, label: "π/2"}, {val: 2*Math.PI/3, label: "2π/3"},
        {val: 3*Math.PI/4, label: "3π/4"}, {val: 5*Math.PI/6, label: "5π/6"}, {val: Math.PI, label: "π"},
        {val: 7*Math.PI/6, label: "7π/6"}, {val: 5*Math.PI/4, label: "5π/4"}, {val: 4*Math.PI/3, label: "4π/3"},
        {val: 3*Math.PI/2, label: "3π/2"}, {val: 5*Math.PI/3, label: "5π/3"}, {val: 7*Math.PI/4, label: "7π/4"},
        {val: 11*Math.PI/6, label: "11π/6"}, {val: 2*Math.PI, label: "2π"}
    ];
    const snapDistance = 0.08; 

    // r計算関数
    function calculateR(angle) {
        if (currentMode === "line_fixed") {
            if (Math.abs(Math.cos(angle)) < 0.001) return 200;
            return 1.0 / Math.cos(angle);
        } 
        else if (currentMode === "circle_origin") {
            return 2.0;
        }
        else if (currentMode === "circle_shifted") {
            return 2.0 * Math.cos(angle);
        }
        return 0;
    }

    function update(rawAngle) {
        let angle = rawAngle;
        if(angle < 0) angle += 2*Math.PI;
        angle = angle % (2*Math.PI + 0.0001);

        // マグネット吸着
        let displayAngleLabel = (angle / Math.PI).toFixed(2) + "π";
        let isSnapped = false;
        
        for (let m of magnets) {
            let diff = Math.abs(angle - m.val);
            if (diff > Math.PI) diff = 2*Math.PI - diff;
            if (diff < snapDistance) {
                angle = m.val;
                displayAngleLabel = m.label;
                isSnapped = true;
                break;
            }
        }

        // --- αモード（直線の回転）の処理 ---
        if (currentMode === "line_alpha") {
            let alpha = angle;
            
            // 1. 直線の描画
            let nx = Math.cos(alpha);
            let ny = -Math.sin(alpha); 
            let dx = -Math.sin(alpha);
            let dy = -Math.cos(alpha); 
            
            let lineLen = 10;
            let x1 = nx + lineLen * dx;
            let y1 = ny + lineLen * dy;
            let x2 = nx - lineLen * dx;
            let y2 = ny - lineLen * dy;
            
            trajectory.setAttribute("d", `M ${x1.toFixed(3)},${y1.toFixed(3)} L ${x2.toFixed(3)},${y2.toFixed(3)}`);
            
            // 2. 垂線の描画
            normalLine.style.display = "block";
            normalLine.setAttribute("x2", nx);
            normalLine.setAttribute("y2", ny);
            
            // 3. 直角マーク
            rightAngle.style.display = "block";
            let s = 0.15; 
            let px = nx - s * Math.cos(alpha);
            let py = ny - s * (-Math.sin(alpha));
            let p2x = px + s * dx; 
            let p2y = py + s * dy;
            let p3x = nx + s * dx;
            let p3y = ny + s * dy;
            rightAngle.setAttribute("d", `M ${nx.toFixed(3)},${ny.toFixed(3)} L ${p3x.toFixed(3)},${p3y.toFixed(3)} L ${p2x.toFixed(3)},${p2y.toFixed(3)} L ${px.toFixed(3)},${py.toFixed(3)}`);

            // 4. ハンドル
            let hx = 2.2 * Math.cos(alpha);
            let hy = -2.2 * Math.sin(alpha);
            handle.setAttribute("cx", hx);
            handle.setAttribute("cy", hy);
            
            // 視線ガイド
            let lx = 6 * Math.cos(alpha);
            let ly = -6 * Math.sin(alpha);
            sightLine.setAttribute("x1", 0); 
            sightLine.setAttribute("y1", 0);
            sightLine.setAttribute("x2", lx);
            sightLine.setAttribute("y2", ly);
            sightLine.style.strokeDasharray = "0.1, 0.1";
            sightLine.setAttribute("stroke", "blue");

            // 5. テキスト情報
            infoAngle.textContent = "α = " + displayAngleLabel;
            infoAngle.setAttribute("fill", "blue");
            infoR.textContent = "d = 1.00 (固定)";
            
            // 不要なものを隠す
            radiusLine.setAttribute("stroke", "none");
            pointP.setAttribute("fill", "none");
            thetaArc.style.display = "none";
            labelTheta.style.display = "none";
            labelR.style.display = "none";
            
            if(isSnapped) {
                infoAngle.style.fontSize = "0.35px";
                handle.setAttribute("r", "0.25");
            } else {
                infoAngle.style.fontSize = "0.28px";
                handle.setAttribute("r", "0.2");
            }
            return; 
        }

        // --- 通常モード（r, θ）の処理 ---
        normalLine.style.display = "none";
        rightAngle.style.display = "none";
        sightLine.setAttribute("x1", -6 * Math.cos(angle)); 
        sightLine.setAttribute("y1", -6 * -Math.sin(angle));
        sightLine.setAttribute("stroke", "#999");
        
        let pathD = "";
        if (currentMode === "line_fixed") {
            pathD = "M 1,-10 L 1,10";
        } else {
            pathD = "M " + (calculateR(0)) + ",0 ";
            const step = 0.05;
            if (angle > 0.01) {
                for(let t=step; t <= angle + 0.02; t += step) {
                    let cappedT = (t > angle) ? angle : t;
                    let r_t = calculateR(cappedT);
                    let x_t = r_t * Math.cos(cappedT);
                    let y_t = -r_t * Math.sin(cappedT);
                    pathD += `L ${x_t.toFixed(3)},${y_t.toFixed(3)} `;
                    if(cappedT >= angle) break;
                }
            }
        }
        trajectory.setAttribute("d", pathD);

        let r = calculateR(angle);
        let drawR = r;
        if (Math.abs(drawR) > 10) drawR = (drawR > 0) ? 10 : -10;

        let px = drawR * Math.cos(angle);
        let py = -drawR * Math.sin(angle);
        let hx = 2.2 * Math.cos(angle);
        let hy = -2.2 * Math.sin(angle); 

        handle.setAttribute("cx", hx);
        handle.setAttribute("cy", hy);

        let lx = 6 * Math.cos(angle);
        let ly = -6 * Math.sin(angle);
        sightLine.setAttribute("x2", lx);
        sightLine.setAttribute("y2", ly);

        radiusLine.setAttribute("stroke", "red"); 
        pointP.setAttribute("fill", "red"); 
        labelR.style.display = "block";

        radiusLine.setAttribute("x2", px);
        radiusLine.setAttribute("y2", py);
        pointP.setAttribute("cx", px);
        pointP.setAttribute("cy", py);
        
        let mainColor = (r >= -0.01) ? "red" : "blue";
        let subColor = (r >= -0.01) ? "none" : "3, 3";
        
        radiusLine.setAttribute("stroke", mainColor);
        radiusLine.setAttribute("stroke-dasharray", subColor);
        pointP.setAttribute("fill", mainColor);
        handle.setAttribute("fill", mainColor);

        infoR.innerHTML = `r = ${r.toFixed(2)}`;
        if (currentMode === "line_fixed" && Math.abs(r) > 50) infoR.innerHTML = "r = ∞";

        if (angle > 0.1) {
            let arcR = 0.6;
            let ax = arcR * Math.cos(angle);
            let ay = -arcR * Math.sin(angle);
            let largeArc = angle > Math.PI ? 1 : 0;
            thetaArc.setAttribute("d", `M${arcR},0 A${arcR},${arcR} 0 ${largeArc},0 ${ax},${ay}`);
            thetaArc.style.display = "block";
            
            let thetaLx = (arcR + 0.2) * Math.cos(angle / 2);
            let thetaLy = -(arcR + 0.2) * Math.sin(angle / 2);
            labelTheta.setAttribute("x", thetaLx);
            labelTheta.setAttribute("y", thetaLy);
            labelTheta.style.display = "block";
        } else {
            thetaArc.style.display = "none";
            labelTheta.style.display = "none";
        }

        let rLabelDist = drawR / 2;
        if (Math.abs(rLabelDist) > 2.2) rLabelDist = (rLabelDist > 0) ? 2.2 : -2.2;
        let rLx = rLabelDist * Math.cos(angle) + 0.1; 
        let rLy = -rLabelDist * Math.sin(angle) - 0.1;
        labelR.setAttribute("x", rLx);
        labelR.setAttribute("y", rLy);
        labelR.setAttribute("fill", mainColor);

        infoAngle.setAttribute("fill", "#333");
        if(isSnapped) {
            infoAngle.setAttribute("fill", "red");
            infoAngle.style.fontSize = "0.35px";
            handle.setAttribute("r", "0.25");
        } else {
            infoAngle.style.fontSize = "0.28px";
            handle.setAttribute("r", "0.2");
        }
        infoAngle.textContent = "θ = " + displayAngleLabel;
    }

    function getAngle(e) {
        const rect = svg.getBoundingClientRect();
        const cx = rect.left + rect.width / 2;
        const cy = rect.top + rect.height / 2;
        const clientX = e.clientX || (e.touches && e.touches[0].clientX);
        const clientY = e.clientY || (e.touches && e.touches[0].clientY);
        if (clientX === undefined) return 0;
        const dx = clientX - cx;
        const dy = clientY - cy;
        let angle = Math.atan2(-dy, dx); 
        if (angle < 0) angle += 2 * Math.PI;
        return angle;
    }

    function onMove(e) {
        if (!isDragging) return;
        if (e.cancelable) e.preventDefault();
        update(getAngle(e));
    }

    function startDrag(e) {
        isDragging = true;
        touchLayer.style.cursor = "grabbing";
        onMove(e);
    }

    function endDrag() {
        isDragging = false;
        touchLayer.style.cursor = "grab";
    }

    touchLayer.addEventListener('mousedown', startDrag);
    touchLayer.addEventListener('touchstart', startDrag, {passive: false});
    window.addEventListener('mousemove', onMove);
    window.addEventListener('touchmove', onMove, {passive: false});
    window.addEventListener('mouseup', endDrag);
    window.addEventListener('touchend', endDrag);

    update(0.001);

</script>
</body>
</html>
"""

html_code = html_template.replace("__MODE_NAME__", mode)
html_code = html_code.replace("__EQUATION_NAME__", equation_choice)

components.html(html_code, height=600)