import streamlit as st
import streamlit.components.v1 as components

# --- ページ設定 ---
st.set_page_config(page_title="極方程式タッチシミュレータ Ultimate", layout="wide")

# --- 【修正】メニューを完全消去する強力なCSS ---
# !important をつけて、iPadなどの強制表示をねじ伏せます
hide_streamlit_style = """
            <style>
            /* ヘッダー全体を隠す */
            header {visibility: hidden !important; opacity: 0 !important; pointer-events: none !important;}
            [data-testid="stHeader"] {visibility: hidden !important; display: none !important;}
            
            /* ツールバー（右上のメニューや右下のプロフィールなど）を隠す */
            [data-testid="stToolbar"] {visibility: hidden !important; display: none !important;}
            [data-testid="stAppDeployButton"] {display: none !important;}
            
            /* ハンバーガーメニューを隠す */
            #MainMenu {visibility: hidden !important; display: none !important;}
            
            /* フッターを隠す */
            footer {visibility: hidden !important; display: none !important;}
            
            /* その他、デコレーション要素を隠す */
            [data-testid="stDecoration"] {visibility: hidden !important; display: none !important;}
            [data-testid="stStatusWidget"] {visibility: hidden !important; display: none !important;}
            </style>
            """
st.markdown(hide_streamlit_style, unsafe_allow_html=True)

# --- タイトルとモード選択 ---
st.markdown("## 極方程式 タッチシミュレータ")
st.markdown("画面をタッチしてグルグル回してください。直線のグラフも途切れずに表示されます。")

# 方程式の選択ラジオボタン
equation_choice = st.radio(
    "表示する極方程式を選んでください:",
    ("r = 2", "rcosθ = 1", "r = 2cosθ"),
    horizontal=True
)

# 選択された方程式をJSに渡すためのモード設定
if equation_choice == "r = 2":
    mode = "circle_origin"
elif equation_choice == "rcosθ = 1":
    mode = "line"
else:
    mode = "circle_shifted"

# --- HTML/JS埋め込みコード ---
html_template = """
<!DOCTYPE html>
<html>
<head>
<style>
    /* 全体の設定 */
    body { 
        font-family: 'Times New Roman', serif;
        user-select: none; 
        -webkit-user-select: none; 
        margin: 0; 
        overflow: hidden; 
        background-color: white; 
        touch-action: none; /* スクロール無効化 */
    }
    #canvas-container { 
        position: relative; 
        width: 100%; 
        max-width: 600px; 
        aspect-ratio: 1 / 1; 
        margin: 0 auto;
        cursor: grab;
    }
    #canvas-container:active { cursor: grabbing; }
    svg { width: 100%; height: 100%; display: block; } 
    
    /* 文字スタイル */
    .axis-label { font-size: 0.2px; fill: #666; font-style: italic; pointer-events: none; }
    /* 数値情報：フォントを少し大きくし、見やすく */
    .status-text { font-size: 0.28px; font-weight: bold; fill: #333; pointer-events: none; font-family: 'Arial'; }
    
    .graph-label { 
        font-size: 0.25px; 
        font-weight: bold; 
        pointer-events: none; 
        text-shadow: 1px 1px 0 #fff, -1px -1px 0 #fff, 1px -1px 0 #fff, -1px 1px 0 #fff;
    }
    
    #eq-display {
        font-size: 0.4px;
        font-weight: bold;
        fill: #333;
        font-family: 'Times New Roman', serif;
        font-style: italic;
        pointer-events: none;
        opacity: 0.8;
    }
    
    /* 線のスタイル */
    .axis { stroke: #000; stroke-width: 0.02; pointer-events: none; }
    
    /* 動く要素 */
    #theta-arc { fill: none; stroke: orange; stroke-width: 0.05; stroke-linecap: round; pointer-events: none; }
    #sight-line { stroke: #999; stroke-width: 0.02; stroke-dasharray: 0.1, 0.1; pointer-events: none; }
    #radius-line { stroke-width: 0.07; stroke-linecap: round; pointer-events: none; }
    #trajectory { fill: none; stroke: black; stroke-width: 0.03; stroke-linecap: round; pointer-events: none; }
    
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

        <text id="eq-display" x="0.5" y="-2.0">__EQUATION_NAME__</text>

        <text id="info-angle" x="-2.4" y="-2.1" class="status-text">θ = 0</text>
        <text id="info-r" x="-2.4" y="-1.8" class="status-text">r = 0.00</text>

        <path id="trajectory" d="M 0,0" />
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
    // Pythonから値を注入する変数
    const currentMode = "__MODE_NAME__"; 

    // 要素取得
    const svg = document.getElementById('main-svg');
    const touchLayer = document.getElementById('touch-layer');
    const handle = document.getElementById('handle');
    const sightLine = document.getElementById('sight-line');
    const radiusLine = document.getElementById('radius-line');
    const pointP = document.getElementById('point-p');
    const thetaArc = document.getElementById('theta-arc');
    const trajectory = document.getElementById('trajectory');
    
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
        if (currentMode === "line") {
            // 直線の場合
            if (Math.abs(Math.cos(angle)) < 0.001) return 200;
            return 1.0 / Math.cos(angle);
        } 
        else if (currentMode === "circle_origin") {
            return 2.0;
        }
        else { // circle_shifted
            return 2.0 * Math.cos(angle);
        }
    }

    // 描画更新
    function update(rawAngle) {
        let angle = rawAngle;
        if(angle < 0) angle += 2*Math.PI;
        angle = angle % (2*Math.PI + 0.0001);

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

        // --- 軌跡更新ロジック ---
        let pathD = "";
        if (currentMode === "line") {
            // 直線の場合は常に「直線x=1」を静的に表示し続ける（途切れ防止）
            pathD = "M 1,-10 L 1,10";
        } 
        else {
            // 円の場合は「ペンの軌跡」を描く
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

        // 座標計算
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
        sightLine.setAttribute("x1", -lx);
        sightLine.setAttribute("y1", -ly);
        sightLine.setAttribute("x2", lx);
        sightLine.setAttribute("y2", ly);

        radiusLine.setAttribute("x2", px);
        radiusLine.setAttribute("y2", py);
        pointP.setAttribute("cx", px);
        pointP.setAttribute("cy", py);
        
        // 色設定
        let mainColor = (r >= -0.01) ? "red" : "blue";
        let subColor = (r >= -0.01) ? "none" : "3, 3";
        
        radiusLine.setAttribute("stroke", mainColor);
        radiusLine.setAttribute("stroke-dasharray", subColor);
        pointP.setAttribute("fill", mainColor);
        handle.setAttribute("fill", mainColor);

        // 情報表示
        infoR.innerHTML = `r = ${r.toFixed(2)}`;
        if (currentMode === "line" && Math.abs(r) > 50) infoR.innerHTML = "r = ∞";

        // 角度マーク
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

        // rラベル
        let rLabelDist = drawR / 2;
        if (Math.abs(rLabelDist) > 2.2) rLabelDist = (rLabelDist > 0) ? 2.2 : -2.2;
        
        let rLx = rLabelDist * Math.cos(angle) + 0.1; 
        let rLy = -rLabelDist * Math.sin(angle) - 0.1;
        
        labelR.setAttribute("x", rLx);
        labelR.setAttribute("y", rLy);
        labelR.setAttribute("fill", mainColor);

        // スナップ時の強調
        if(isSnapped) {
            infoAngle.setAttribute("fill", "red");
            infoAngle.style.fontSize = "0.35px";
            handle.setAttribute("r", "0.25");
        } else {
            infoAngle.setAttribute("fill", "#333");
            infoAngle.style.fontSize = "0.28px";
            handle.setAttribute("r", "0.2");
        }
        infoAngle.textContent = "θ = " + displayAngleLabel;
    }

    // イベント系
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

    update(0.001); // 初期描画

</script>
</body>
</html>
"""

# Python変数をHTML内のプレースホルダーに埋め込む
html_code = html_template.replace("__MODE_NAME__", mode)
html_code = html_code.replace("__EQUATION_NAME__", equation_choice)

# HTMLを描画
components.html(html_code, height=600)