/**
 * Tic-Tac-Toe: Minimax & Alpha-Beta Pruning Interactive Web App
 * Handles game state, UI rendering, tree visualization, chart, divider, and fullscreen mode.
 * Theme: Exact #3d1515.
 */

document.addEventListener('DOMContentLoaded', () => {
  // --- Game State ---
  let board = Array(9).fill('');
  let isGameOver = false;
  let isHumanTurn = true;
  let starter = 'human'; // 'human' or 'ai'
  let moveNumber = 0;

  // Persistent Scores
  const scores = {
    human: parseInt(localStorage.getItem('ttt_human_wins') || '0', 10),
    ai: parseInt(localStorage.getItem('ttt_ai_wins') || '0', 10),
    draws: parseInt(localStorage.getItem('ttt_draws') || '0', 10),
  };

  // Performance history across moves in current game
  let moveHistory = [];
  let currentStats = null;
  let currentTree = null;
  let treeFocusNode = null;
  let activeTab = 'move'; // 'move' or 'game'
  let fullscreenMode = null; // 'tree' | 'chart' | null

  // --- DOM Elements ---
  const boardEl = document.getElementById('gameBoard');
  const cells = document.querySelectorAll('.cell');
  const statusMsgEl = document.getElementById('statusMessage');
  const turnBadgeEl = document.getElementById('turnBadge');
  const turnTextEl = document.getElementById('turnText');
  const newGameBtn = document.getElementById('newGameBtn');
  const resetScoreBtn = document.getElementById('resetScoreBtn');
  const algorithmSelect = document.getElementById('algorithmSelect');
  const difficultySelect = document.getElementById('difficultySelect');
  const starterSelect = document.getElementById('starterSelect');

  // Scores
  const humanWinsVal = document.getElementById('humanWinsVal');
  const aiWinsVal = document.getElementById('aiWinsVal');
  const drawsVal = document.getElementById('drawsVal');

  // Comparison Table
  const perfViewBadge = document.getElementById('perfViewBadge');
  const mmNodesCell = document.getElementById('mmNodesCell');
  const abNodesCell = document.getElementById('abNodesCell');
  const mmTimeCell = document.getElementById('mmTimeCell');
  const abTimeCell = document.getElementById('abTimeCell');
  const mmPrunedCell = document.getElementById('mmPrunedCell');
  const abPrunedCell = document.getElementById('abPrunedCell');
  const mmEffCell = document.getElementById('mmEffCell');
  const abEffCell = document.getElementById('abEffCell');
  const tabMoveBtn = document.getElementById('tabMoveBtn');
  const tabGameBtn = document.getElementById('tabGameBtn');

  // Tree Visualizer
  const treeSvg = document.getElementById('treeSvg');
  const treePlaceholder = document.getElementById('treeEmptyMessage');
  const resetTreeFocusBtn = document.getElementById('resetTreeFocusBtn');
  const fullscreenTreeBtn = document.getElementById('fullscreenTreeBtn');
  const treeTooltip = document.getElementById('treeTooltip');


  // Candidate Moves
  const candidateListEl = document.getElementById('candidateList');
  const miniCells = document.querySelectorAll('.mini-cell');

  // Chart
  const nodeChartSvg = document.getElementById('nodeChartSvg');
  const fullscreenChartBtn = document.getElementById('fullscreenChartBtn');

  // Layout, Nav, and Divider
  const appLayout = document.getElementById('appLayout');
  const leftPane = document.getElementById('leftPane');
  const rightPane = document.getElementById('rightPane');
  const paneDivider = document.getElementById('paneDivider');
  const toggleAnalysisBtn = document.getElementById('toggleAnalysisBtn');
  const closeAnalysisBtn = document.getElementById('closeAnalysisBtn');
  const collapseBtn = document.getElementById('collapseBtn');
  const expandBtn = document.getElementById('expandBtn');

  // Fullscreen Modal Elements
  const fullscreenModal = document.getElementById('fullscreenModal');
  const fullscreenTitle = document.getElementById('fullscreenTitle');
  const fullscreenSubtitle = document.getElementById('fullscreenSubtitle');
  const fullscreenBody = document.getElementById('fullscreenBody');
  const exitFullscreenBtn = document.getElementById('exitFullscreenBtn');
  const fullscreenResetFocusBtn = document.getElementById('fullscreenResetFocusBtn');

  // --- Initial Setup ---
  updateScoreboardUI();
  initAnalysisToggle();
  initDividerDragging();
  initFullscreenHandlers();
  initControls();
  resetGame();

  // ==========================================================================
  // One-Click Toggle for AI Analysis (Center vs Split View)
  // ==========================================================================
  function initAnalysisToggle() {
    function setAnalysisOpen(isOpen) {
      if (isOpen) {
        appLayout.classList.add('analysis-open');
        toggleAnalysisBtn.innerHTML = '<span class="toggle-icon">✕</span><span class="toggle-label">Hide AI Analysis</span>';
        leftPane.style.flex = '0 0 46%';
        leftPane.style.maxWidth = '55%';
        setTimeout(() => {
          if (currentTree) renderTreeSvg(treeFocusNode || currentTree, treeSvg);
          renderChartSvg(nodeChartSvg);
        }, 150);
      } else {
        appLayout.classList.remove('analysis-open');
        toggleAnalysisBtn.innerHTML = '<span class="toggle-icon">📊</span><span class="toggle-label">View AI Analysis</span>';
        leftPane.style.flex = '1 1 100%';
        leftPane.style.maxWidth = '100%';
      }
    }

    toggleAnalysisBtn.addEventListener('click', () => {
      const isCurrentlyOpen = appLayout.classList.contains('analysis-open');
      setAnalysisOpen(!isCurrentlyOpen);
    });

    if (closeAnalysisBtn) {
      closeAnalysisBtn.addEventListener('click', () => {
        setAnalysisOpen(false);
      });
    }

    if (collapseBtn) {
      collapseBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        setAnalysisOpen(false);
      });
    }

    if (expandBtn) {
      expandBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        setAnalysisOpen(true);
      });
    }
  }

  // ==========================================================================
  // Divider Dragging with Tight Boundaries
  // ==========================================================================
  function initDividerDragging() {
    let isDragging = false;

    paneDivider.addEventListener('mousedown', (e) => {
      if (e.target.closest('.divider-arrow')) return;
      isDragging = true;
      paneDivider.classList.add('dragging');
      document.body.style.cursor = 'col-resize';
      e.preventDefault();
    });

    window.addEventListener('mousemove', (e) => {
      if (!isDragging) return;
      const containerWidth = appLayout.getBoundingClientRect().width;

      const minLeft = Math.round(containerWidth * 0.42);
      const maxLeft = Math.round(containerWidth * 0.55);
      let newLeftWidth = e.clientX;

      if (newLeftWidth < minLeft) newLeftWidth = minLeft;
      if (newLeftWidth > maxLeft) newLeftWidth = maxLeft;

      leftPane.style.flex = `0 0 ${newLeftWidth}px`;
      leftPane.style.maxWidth = `${newLeftWidth}px`;
    });

    window.addEventListener('mouseup', () => {
      if (isDragging) {
        isDragging = false;
        paneDivider.classList.remove('dragging');
        document.body.style.cursor = 'default';
        if (currentTree) renderTreeSvg(treeFocusNode || currentTree, treeSvg);
        renderChartSvg(nodeChartSvg);
      }
    });
  }

  // ==========================================================================
  // Fullscreen Graph & Chart Handlers
  // ==========================================================================
  function initFullscreenHandlers() {
    fullscreenTreeBtn.addEventListener('click', () => {
      openFullscreen('tree');
    });

    fullscreenChartBtn.addEventListener('click', () => {
      openFullscreen('chart');
    });

    exitFullscreenBtn.addEventListener('click', closeFullscreen);

    fullscreenResetFocusBtn.addEventListener('click', () => {
      treeFocusNode = null;
      fullscreenResetFocusBtn.style.display = 'none';
      renderFullscreenContent();
    });

    window.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && fullscreenMode) {
        closeFullscreen();
      }
    });
  }

  // Hover Tooltip Display Logic
  function showNodeTooltip(e, node) {
    if (!treeTooltip) return;
    const isMax = node.type === 'MAX';
    const moveStr = node.move !== null && node.move !== undefined ? `Move: Cell ${node.move}` : 'Root (AI)';
    const scoreVal = node.pruned ? 'Pruned (Cutoff)' : (node.score !== null ? (node.score > 0 ? `+${node.score}` : `${node.score}`) : '—');

    let badgeHtml = '';
    if (node.chosen) {
      badgeHtml = '<div class="tt-badge chosen">★ Chosen Move</div>';
    } else if (node.pruned) {
      badgeHtml = '<div class="tt-badge pruned">✂ Cutoff (β ≤ α)</div>';
    }

    let boundsHtml = '';
    if (node.alpha !== 'N/A' && node.alpha !== null && node.alpha !== undefined) {
      boundsHtml = `
        <div class="tt-row"><span>Alpha (α):</span> <strong>${node.alpha}</strong></div>
        <div class="tt-row"><span>Beta (β):</span> <strong>${node.beta}</strong></div>
      `;
    } else {
      boundsHtml = `
        <div class="tt-row"><span>Search Mode:</span> <strong>Minimax (Full Evaluation)</strong></div>
        <div class="tt-row"><span>Pruning:</span> <strong>Disabled (0 Cutoffs)</strong></div>
      `;
    }

    treeTooltip.innerHTML = `
      <div class="tt-header">
        <span class="tt-name ${isMax ? 'max' : 'min'}">${node.type} (${node.player})</span>
        <span class="tt-move">${moveStr}</span>
      </div>
      <div class="tt-row"><span>Score:</span> <strong>${scoreVal}</strong></div>
      ${boundsHtml}
      ${badgeHtml}
    `;

    treeTooltip.style.display = 'flex';
    positionTooltip(e);
  }

  function positionTooltip(e) {
    if (!treeTooltip || treeTooltip.style.display === 'none') return;

    // Get live tooltip dimensions
    const tooltipWidth = treeTooltip.offsetWidth || 190;
    const tooltipHeight = treeTooltip.offsetHeight || 130;
    const viewportWidth = window.innerWidth;
    const viewportHeight = window.innerHeight;

    // Default positioning: to the right and slightly below cursor
    let posX = e.clientX + 16;
    let posY = e.clientY + 14;

    // Boundary check right edge: if overflowing, flip to the left of the cursor
    if (posX + tooltipWidth > viewportWidth - 16) {
      posX = e.clientX - tooltipWidth - 16;
    }

    // Boundary check bottom edge: if overflowing, flip above the cursor
    if (posY + tooltipHeight > viewportHeight - 16) {
      posY = e.clientY - tooltipHeight - 14;
    }

    // Safety clamp to ensure the tooltip is 100% visible inside the viewport
    posX = Math.max(12, Math.min(posX, viewportWidth - tooltipWidth - 12));
    posY = Math.max(12, Math.min(posY, viewportHeight - tooltipHeight - 12));

    treeTooltip.style.left = `${posX}px`;
    treeTooltip.style.top = `${posY}px`;
  }

  function hideNodeTooltip() {
    if (treeTooltip) treeTooltip.style.display = 'none';
  }

  function openFullscreen(mode) {
    fullscreenMode = mode;
    fullscreenModal.style.display = 'flex';

    if (mode === 'tree') {
      fullscreenTitle.textContent = '🌳 Decision Tree Visualization (Fullscreen)';
      fullscreenSubtitle.textContent = 'Hover over any node to view details (name, move, score, bounds)';
      fullscreenResetFocusBtn.style.display = treeFocusNode ? 'inline-block' : 'none';
    } else {
      fullscreenTitle.textContent = '📈 Nodes Explored Comparison (Fullscreen)';
      fullscreenSubtitle.textContent = 'Historical Search Volume per Move: Minimax vs Alpha-Beta Pruning';
      fullscreenResetFocusBtn.style.display = 'none';
    }

    renderFullscreenContent();
  }

  function closeFullscreen() {
    fullscreenMode = null;
    fullscreenModal.style.display = 'none';
    fullscreenBody.innerHTML = '';
    hideNodeTooltip();
    // Re-render standard embedded views
    if (currentTree) renderTreeSvg(treeFocusNode || currentTree, treeSvg);
    renderChartSvg(nodeChartSvg);
  }


  function renderFullscreenContent() {
    fullscreenBody.innerHTML = '';

    if (fullscreenMode === 'tree') {
      if (!currentTree) {
        fullscreenBody.innerHTML = '<div style="color: #9aa0a6; text-align: center; font-size: 16px;">Make a move to see live tree data.</div>';
        return;
      }
      const fsSvg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      fsSvg.setAttribute('class', 'fullscreen-tree-svg');
      fullscreenBody.appendChild(fsSvg);

      const targetNode = treeFocusNode || currentTree;
      renderTreeSvg(targetNode, fsSvg, true);

      fullscreenResetFocusBtn.style.display = treeFocusNode && treeFocusNode !== currentTree ? 'inline-block' : 'none';
    } else if (fullscreenMode === 'chart') {
      const fsSvg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
      fsSvg.setAttribute('class', 'fullscreen-chart-svg');
      fullscreenBody.appendChild(fsSvg);
      renderChartSvg(fsSvg, true);
    }
  }


  // ==========================================================================
  // UI & Score Management
  // ==========================================================================
  function updateScoreboardUI() {
    humanWinsVal.textContent = scores.human;
    aiWinsVal.textContent = scores.ai;
    drawsVal.textContent = scores.draws;
  }

  function saveScores() {
    localStorage.setItem('ttt_human_wins', scores.human);
    localStorage.setItem('ttt_ai_wins', scores.ai);
    localStorage.setItem('ttt_draws', scores.draws);
    updateScoreboardUI();
  }

  resetScoreBtn.addEventListener('click', () => {
    scores.human = 0;
    scores.ai = 0;
    scores.draws = 0;
    saveScores();
  });

  function initControls() {
    newGameBtn.addEventListener('click', resetGame);

    starterSelect.addEventListener('change', () => {
      starter = starterSelect.value;
      resetGame();
    });

    tabMoveBtn.addEventListener('click', () => {
      activeTab = 'move';
      tabMoveBtn.classList.add('active');
      tabGameBtn.classList.remove('active');
      renderComparisonTable();
    });

    tabGameBtn.addEventListener('click', () => {
      activeTab = 'game';
      tabGameBtn.classList.add('active');
      tabMoveBtn.classList.remove('active');
      renderComparisonTable();
    });

    resetTreeFocusBtn.addEventListener('click', () => {
      treeFocusNode = null;
      resetTreeFocusBtn.style.display = 'none';
      if (currentTree) renderTreeSvg(currentTree, treeSvg);
    });


    cells.forEach((cell) => {
      cell.addEventListener('click', () => {
        const index = parseInt(cell.getAttribute('data-index'), 10);
        handleHumanMove(index);
      });
    });
  }

  // ==========================================================================
  // Game Actions
  // ==========================================================================
  function resetGame() {
    board = Array(9).fill('');
    isGameOver = false;
    moveNumber = 0;
    moveHistory = [];
    currentStats = null;
    currentTree = null;
    treeFocusNode = null;
    resetTreeFocusBtn.style.display = 'none';

    cells.forEach((cell) => {
      cell.textContent = '';
      cell.className = 'cell';
      cell.disabled = false;
    });

    clearAnalysisUI();

    starter = starterSelect.value;
    if (starter === 'ai') {
      isHumanTurn = false;
      updateTurnStatus('AI thinking...', false);
      setTimeout(() => triggerAiMove(null), 300);
    } else {
      isHumanTurn = true;
      updateTurnStatus('Your turn (Click an empty square)', true);
    }
  }

  function updateTurnStatus(msg, isHuman) {
    statusMsgEl.textContent = msg;
    if (isGameOver) {
      turnBadgeEl.style.display = 'none';
    } else {
      turnBadgeEl.style.display = 'inline-flex';
      turnTextEl.textContent = isHuman ? 'Your Turn' : 'AI Thinking...';
      const dot = turnBadgeEl.querySelector('.indicator-dot');
      if (dot) {
        dot.style.background = isHuman ? '#4ade80' : '#ff5252';
        dot.style.boxShadow = isHuman ? '0 0 8px #4ade80' : '0 0 8px #ff5252';
      }
    }
  }

  function handleHumanMove(cellIndex) {
    if (!isHumanTurn || isGameOver || board[cellIndex] !== '') return;

    cells[cellIndex].textContent = 'X';
    cells[cellIndex].classList.add('cell-x');
    cells[cellIndex].disabled = true;

    isHumanTurn = false;
    updateTurnStatus('AI thinking...', false);

    triggerAiMove(cellIndex);
  }

  async function triggerAiMove(humanMoveIndex) {
    const payload = {
      board: board,
      human_move: humanMoveIndex,
      algorithm: algorithmSelect.value,
      difficulty: difficultySelect.value,
      ai_first: starter === 'ai' && humanMoveIndex === null,
    };

    try {
      const response = await fetch('/api/move', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      if (!response.ok) {
        const err = await response.json();
        console.error('API Error:', err);
        updateTurnStatus(err.error || 'Move error. Please retry.', true);
        isHumanTurn = true;
        if (humanMoveIndex !== null) {
          cells[humanMoveIndex].textContent = '';
          cells[humanMoveIndex].className = 'cell';
          cells[humanMoveIndex].disabled = false;
        }
        return;
      }

      const data = await response.json();
      handleMoveResponse(data);
    } catch (err) {
      console.error('Network Error:', err);
      updateTurnStatus('Connection error. Please retry.', true);
      isHumanTurn = true;
      if (humanMoveIndex !== null) {
        cells[humanMoveIndex].textContent = '';
        cells[humanMoveIndex].className = 'cell';
        cells[humanMoveIndex].disabled = false;
      }
    }
  }

  function handleMoveResponse(data) {
    board = data.board;
    moveNumber++;

    board.forEach((val, idx) => {
      cells[idx].textContent = val;
      if (val === 'X') cells[idx].className = 'cell cell-x';
      else if (val === 'O') cells[idx].className = 'cell cell-o';
      else cells[idx].className = 'cell';
      cells[idx].disabled = val !== '' || data.is_game_over;
    });

    if (data.is_game_over) {
      isGameOver = true;
      if (data.winning_line) {
        data.winning_line.forEach((idx) => {
          cells[idx].classList.add('cell-win');
        });
      }

      if (data.game_status === 'human_win') {
        scores.human++;
        saveScores();
        updateTurnStatus('🎉 Congratulations! You won!', true);
      } else if (data.game_status === 'ai_win') {
        scores.ai++;
        saveScores();
        updateTurnStatus('🤖 AI Wins! Better luck next time.', false);
      } else {
        scores.draws++;
        saveScores();
        updateTurnStatus("🤝 It's a draw!", false);
      }
    } else {
      isHumanTurn = true;
      updateTurnStatus('Your turn (Click an empty square)', true);
    }

    if (data.minimax_stats && data.alphabeta_stats) {
      currentStats = {
        moveNumber: moveNumber,
        mmNodes: data.minimax_stats.nodes_explored,
        abNodes: data.alphabeta_stats.nodes_explored,
        mmTime: data.minimax_stats.execution_time_ms,
        abTime: data.alphabeta_stats.execution_time_ms,
        pruned: data.alphabeta_stats.branches_pruned,
        efficiency: data.efficiency.percent_fewer_nodes,
      };

      moveHistory.push(currentStats);

      currentTree = data.decision_tree;
      treeFocusNode = null;
      resetTreeFocusBtn.style.display = 'none';

      renderComparisonTable();
      renderCandidateMoves(data.candidate_moves);
      renderTreeSvg(currentTree, treeSvg);
      renderChartSvg(nodeChartSvg);

      if (fullscreenMode) {
        renderFullscreenContent();
      }
    }
  }

  // ==========================================================================
  // Right Pane: Analysis Renderers
  // ==========================================================================
  function clearAnalysisUI() {
    mmNodesCell.textContent = '—';
    abNodesCell.textContent = '—';
    mmTimeCell.textContent = '—';
    abTimeCell.textContent = '—';
    mmPrunedCell.textContent = '0';
    abPrunedCell.textContent = '—';
    mmEffCell.textContent = '0.0%';
    abEffCell.textContent = '—';
    perfViewBadge.textContent = 'Move #1';

    candidateListEl.innerHTML = '<div class="candidate-empty">No moves evaluated yet</div>';
    miniCells.forEach((c) => {
      c.innerHTML = '';
      c.className = 'mini-cell';
    });

    treePlaceholder.style.display = 'flex';
    treeSvg.innerHTML = '';
    nodeChartSvg.innerHTML = '';
  }

  function renderComparisonTable() {
    if (!currentStats && moveHistory.length === 0) return;

    if (activeTab === 'move') {
      perfViewBadge.textContent = `Move #${currentStats.moveNumber}`;
      mmNodesCell.textContent = currentStats.mmNodes.toLocaleString();
      abNodesCell.textContent = currentStats.abNodes.toLocaleString();
      mmTimeCell.textContent = `${currentStats.mmTime.toFixed(2)} ms`;
      abTimeCell.textContent = `${currentStats.abTime.toFixed(2)} ms`;
      mmPrunedCell.textContent = '0';
      abPrunedCell.textContent = currentStats.pruned.toLocaleString();
      mmEffCell.textContent = '0.0%';
      abEffCell.textContent = `${currentStats.efficiency.toFixed(1)}% fewer nodes`;
    } else {
      const totalMmNodes = moveHistory.reduce((sum, m) => sum + m.mmNodes, 0);
      const totalAbNodes = moveHistory.reduce((sum, m) => sum + m.abNodes, 0);
      const totalMmTime = moveHistory.reduce((sum, m) => sum + m.mmTime, 0);
      const totalAbTime = moveHistory.reduce((sum, m) => sum + m.abTime, 0);
      const totalPruned = moveHistory.reduce((sum, m) => sum + m.pruned, 0);
      const cumulativeEff =
        totalMmNodes > 0
          ? (((totalMmNodes - totalAbNodes) / totalMmNodes) * 100).toFixed(1)
          : '0.0';

      perfViewBadge.textContent = `Cumulative (${moveHistory.length} Moves)`;
      mmNodesCell.textContent = totalMmNodes.toLocaleString();
      abNodesCell.textContent = totalAbNodes.toLocaleString();
      mmTimeCell.textContent = `${totalMmTime.toFixed(2)} ms`;
      abTimeCell.textContent = `${totalAbTime.toFixed(2)} ms`;
      mmPrunedCell.textContent = '0';
      abPrunedCell.textContent = totalPruned.toLocaleString();
      mmEffCell.textContent = '0.0%';
      abEffCell.textContent = `${cumulativeEff}% fewer nodes`;
    }
  }

  function renderCandidateMoves(candidates) {
    if (!candidates || candidates.length === 0) return;

    miniCells.forEach((mc, idx) => {
      mc.innerHTML = '';
      mc.className = 'mini-cell';

      const cellVal = board[idx];
      if (cellVal !== '') {
        mc.textContent = cellVal;
        mc.classList.add('mini-occupied');
      } else {
        const cand = candidates.find((c) => c.move === idx);
        if (cand) {
          const scoreFmt = cand.score > 0 ? `+${cand.score}` : `${cand.score}`;
          mc.innerHTML = `<span class="cand-score">${scoreFmt}</span>`;
          if (cand.chosen) {
            mc.classList.add('mini-chosen');
          }
        }
      }
    });

    candidateListEl.innerHTML = '';
    const sorted = [...candidates].sort((a, b) => {
      if (a.chosen && !b.chosen) return -1;
      if (!a.chosen && b.chosen) return 1;
      return b.score - a.score;
    });

    sorted.forEach((cand) => {
      const item = document.createElement('div');
      item.className = `candidate-item ${cand.chosen ? 'is-chosen' : ''}`;

      const scoreFormatted = cand.score > 0 ? `+${cand.score}` : `${cand.score}`;
      const statusHtml = cand.chosen
        ? '<span class="status-tag chosen-tag">★ Chosen</span>'
        : '<span class="status-tag">Evaluated</span>';

      item.innerHTML = `
        <span>Cell ${cand.move} (r${cand.row}, c${cand.col})</span>
        <span style="font-weight: 700; color: ${cand.score > 0 ? '#ff7575' : cand.score < 0 ? '#64b5f6' : '#b0bec5'}">
          ${scoreFormatted}
        </span>
        <span>${statusHtml}</span>
      `;
      candidateListEl.appendChild(item);
    });
  }

  // ==========================================================================
  // Section B: Interactive Decision Tree Visualization
  // ==========================================================================
  function renderTreeSvg(rootNode, targetSvgEl, isFullscreen = false) {
    if (!rootNode || !targetSvgEl) return;
    if (targetSvgEl === treeSvg) treePlaceholder.style.display = 'none';
    targetSvgEl.innerHTML = '';

    const children = rootNode.children || [];
    const childCount = children.length;
    const isShowingFocusedSubtree = (treeFocusNode !== null);

    const baseWidth = isFullscreen ? Math.max(1200, window.innerWidth - 80) : Math.max(700, targetSvgEl.parentElement.clientWidth);
    const height = isFullscreen ? Math.max(540, window.innerHeight - 200) : 320;

    targetSvgEl.setAttribute('viewBox', `0 0 ${baseWidth} ${height}`);
    targetSvgEl.style.minWidth = isFullscreen ? '1100px' : '650px';

    if (!isFullscreen) {
      if (treeFocusNode && treeFocusNode !== currentTree) {
        resetTreeFocusBtn.style.display = 'inline-block';
      } else {
        resetTreeFocusBtn.style.display = 'none';
      }
    }

    const rootX = baseWidth / 2;
    const rootY = isFullscreen ? 55 : 44;

    // Draw Root Node
    drawTreeNode(targetSvgEl, rootNode, rootX, rootY, false, null, isFullscreen ? 30 : 24, true);
    if (childCount === 0) return;

    const paddingX = isFullscreen ? 90 : 50;
    const availableWidth = baseWidth - paddingX * 2;
    const stepX = childCount > 1 ? availableWidth / (childCount - 1) : availableWidth / 2;
    const level1Y = rootY + (isFullscreen ? 135 : 100);

    children.forEach((child, idx) => {
      const childX = childCount === 1 ? baseWidth / 2 : paddingX + idx * stepX;
      const childY = level1Y;

      drawTreeEdge(targetSvgEl, rootX, rootY, childX, childY, child.chosen, isFullscreen ? 30 : 24);

      // Candidate Move (Level 1) Node
      drawTreeNode(targetSvgEl, child, childX, childY, true, () => {
        if (child.children && child.children.length > 0) {
          treeFocusNode = child;
          if (isFullscreen) {
            renderFullscreenContent();
          } else {
            renderTreeSvg(child, treeSvg);
          }
        }
      }, isFullscreen ? 24 : 19, true);

      // Grandchildren (Sub-moves) - Drawn cleanly with NO colliding text
      const grandChildren = child.children || [];
      const gcCount = grandChildren.length;
      if (gcCount > 0) {
        const gcWidth = isShowingFocusedSubtree
          ? Math.min(baseWidth - 140, gcCount * (isFullscreen ? 120 : 80))
          : Math.min(stepX * 0.95, isFullscreen ? 140 : 85);
        const gcStartX = childX - gcWidth / 2;
        const gcStep = gcCount > 1 ? gcWidth / (gcCount - 1) : gcWidth / 2;
        const level2Y = childY + (isFullscreen ? 130 : 95);

        grandChildren.forEach((gc, gcIdx) => {
          const gcX = gcCount === 1 ? childX : gcStartX + gcIdx * gcStep;
          const gcY = level2Y;

          drawTreeEdge(targetSvgEl, childX, childY, gcX, gcY, gc.chosen, isFullscreen ? 16 : 12);
          // showLabel = false for grandchildren to keep tree completely unclustered!
          drawTreeNode(targetSvgEl, gc, gcX, gcY, false, null, isFullscreen ? 15 : 11, false);
        });
      }
    });
  }

  function drawTreeEdge(targetSvg, x1, y1, x2, y2, isChosen, radius = 20) {
    const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
    line.setAttribute('x1', x1);
    line.setAttribute('y1', y1 + radius - 4);
    line.setAttribute('x2', x2);
    line.setAttribute('y2', y2 - radius + 4);
    line.setAttribute('class', `tree-edge ${isChosen ? 'chosen-edge' : ''}`);
    targetSvg.appendChild(line);
  }

  function drawTreeNode(targetSvg, node, cx, cy, isClickable = false, onClickCallback = null, radius = 20, showLabel = true) {
    const group = document.createElementNS('http://www.w3.org/2000/svg', 'g');
    group.setAttribute('class', 'tree-node-group');

    // Attach mouse hover events for sleek details popup
    group.addEventListener('mouseenter', (e) => showNodeTooltip(e, node));
    group.addEventListener('mousemove', (e) => positionTooltip(e));
    group.addEventListener('mouseleave', hideNodeTooltip);

    const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
    circle.setAttribute('cx', cx);
    circle.setAttribute('cy', cy);
    circle.setAttribute('r', radius);

    let circleClasses = 'tree-node-circle ';
    circleClasses += node.pruned ? 'dashed ' : 'solid ';
    if (node.chosen) circleClasses += 'chosen ';
    circle.setAttribute('class', circleClasses);
    group.appendChild(circle);

    // Number / Score inside node
    const scoreText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
    scoreText.setAttribute('x', cx);
    scoreText.setAttribute('y', cy - 1);
    scoreText.setAttribute('class', 'tree-node-score');
    if (radius < 14) scoreText.setAttribute('font-size', '8px');
    else if (radius < 18) scoreText.setAttribute('font-size', '9.5px');
    else if (radius >= 26) scoreText.setAttribute('font-size', '13px');

    if (node.pruned) {
      scoreText.textContent = '✂';
      scoreText.style.fill = '#88978b';
    } else if (node.score !== null) {
      scoreText.textContent = node.score > 0 ? `+${node.score}` : `${node.score}`;
      if (node.score > 0) scoreText.style.fill = '#ff8585';
      else if (node.score < 0) scoreText.style.fill = '#64b5f6';
      else scoreText.style.fill = '#ffffff';
    } else {
      scoreText.textContent = '?';
    }
    group.appendChild(scoreText);

    // Clean label above node (Only for Root and Level 1 candidate moves)
    if (showLabel) {
      const labelText = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      labelText.setAttribute('x', cx);
      labelText.setAttribute('y', cy - radius - 7);
      labelText.setAttribute('class', 'tree-node-text');
      if (radius < 18) labelText.setAttribute('font-size', '8.5px');
      else if (radius >= 26) labelText.setAttribute('font-size', '11.5px');

      const prefix = node.move !== null && node.move !== undefined ? `m${node.move}` : 'AI';
      const chosenStar = node.chosen ? ' ★' : '';
      labelText.textContent = `${node.type} [${prefix}]${chosenStar}`;
      if (node.type === 'MAX') labelText.style.fill = '#ff8585';
      else labelText.style.fill = '#90caf9';
      group.appendChild(labelText);
    }

    if (isClickable && onClickCallback) {
      group.style.cursor = 'pointer';
      group.addEventListener('click', onClickCallback);
    }

    targetSvg.appendChild(group);
  }


  // ==========================================================================
  // Section E: SVG Bar Chart (Nodes Explored: MM vs AB)
  // ==========================================================================
  function renderChartSvg(targetSvg, isFullscreen = false) {
    if (moveHistory.length === 0 || !targetSvg) return;
    targetSvg.innerHTML = '';

    const width = isFullscreen ? Math.max(900, window.innerWidth - 120) : 500;
    const height = isFullscreen ? Math.max(420, window.innerHeight - 240) : 180;
    targetSvg.setAttribute('viewBox', `0 0 ${width} ${height}`);

    const paddingLeft = isFullscreen ? 80 : 60;
    const paddingRight = 30;
    const paddingTop = 25;
    const paddingBottom = 35;

    const chartWidth = width - paddingLeft - paddingRight;
    const chartHeight = height - paddingTop - paddingBottom;
    const maxVal = Math.max(...moveHistory.map((m) => Math.max(m.mmNodes, m.abNodes)), 100);

    const gridCount = 4;
    for (let i = 0; i <= gridCount; i++) {
      const y = paddingTop + (chartHeight / gridCount) * i;
      const val = Math.round(maxVal - (maxVal / gridCount) * i);

      const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
      line.setAttribute('x1', paddingLeft);
      line.setAttribute('y1', y);
      line.setAttribute('x2', width - paddingRight);
      line.setAttribute('y2', y);
      line.setAttribute('stroke', '#2d3033');
      line.setAttribute('stroke-dasharray', '2, 3');
      targetSvg.appendChild(line);

      const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      text.setAttribute('x', paddingLeft - 8);
      text.setAttribute('y', y + 3);
      text.setAttribute('text-anchor', 'end');
      text.setAttribute('font-size', isFullscreen ? '12px' : '10px');
      text.setAttribute('fill', '#889199');
      text.setAttribute('font-family', 'var(--font-mono)');
      text.textContent = val >= 1000 ? `${(val / 1000).toFixed(0)}k` : `${val}`;
      targetSvg.appendChild(text);
    }

    const groupWidth = chartWidth / moveHistory.length;
    const barWidth = Math.min(groupWidth * 0.35, isFullscreen ? 45 : 26);

    moveHistory.forEach((item, idx) => {
      const groupCenterX = paddingLeft + idx * groupWidth + groupWidth / 2;

      // Minimax bar
      const mmH = Math.max((item.mmNodes / maxVal) * chartHeight, 2);
      const mmY = paddingTop + (chartHeight - mmH);
      const mmX = groupCenterX - barWidth - 3;

      const mmRect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
      mmRect.setAttribute('x', mmX);
      mmRect.setAttribute('y', mmY);
      mmRect.setAttribute('width', barWidth);
      mmRect.setAttribute('height', mmH);
      mmRect.setAttribute('fill', '#78909c');
      mmRect.setAttribute('rx', '3');

      const mmTitle = document.createElementNS('http://www.w3.org/2000/svg', 'title');
      mmTitle.textContent = `Move #${item.moveNumber} - Minimax: ${item.mmNodes.toLocaleString()} nodes`;
      mmRect.appendChild(mmTitle);
      targetSvg.appendChild(mmRect);

      // Alpha-Beta bar
      const abH = Math.max((item.abNodes / maxVal) * chartHeight, 2);
      const abY = paddingTop + (chartHeight - abH);
      const abX = groupCenterX + 3;

      const abRect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
      abRect.setAttribute('x', abX);
      abRect.setAttribute('y', abY);
      abRect.setAttribute('width', barWidth);
      abRect.setAttribute('height', abH);
      abRect.setAttribute('fill', '#c73c3c');
      abRect.setAttribute('rx', '3');

      const abTitle = document.createElementNS('http://www.w3.org/2000/svg', 'title');
      abTitle.textContent = `Move #${item.moveNumber} - Alpha-Beta: ${item.abNodes.toLocaleString()} nodes (${item.efficiency}% fewer)`;
      abRect.appendChild(abTitle);
      targetSvg.appendChild(abRect);

      // X-axis label
      const xLabel = document.createElementNS('http://www.w3.org/2000/svg', 'text');
      xLabel.setAttribute('x', groupCenterX);
      xLabel.setAttribute('y', height - 8);
      xLabel.setAttribute('text-anchor', 'middle');
      xLabel.setAttribute('font-size', isFullscreen ? '12px' : '10px');
      xLabel.setAttribute('font-weight', '600');
      xLabel.setAttribute('fill', '#9aa0a6');
      xLabel.textContent = `M${item.moveNumber}`;
      targetSvg.appendChild(xLabel);
    });
  }
});
