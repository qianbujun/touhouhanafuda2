const socket = io();

// UI Elements
const lobbyScreen = document.getElementById('lobby-screen');
const roomScreen = document.getElementById('room-screen');
const gameScreen = document.getElementById('game-screen');

const loginSection = document.getElementById('login-section');
const roomsSection = document.getElementById('rooms-section');
const usernameInput = document.getElementById('username-input');
const setNameBtn = document.getElementById('set-name-btn');
const displayName = document.getElementById('display-name');
const createRoomBtn = document.getElementById('create-room-btn');
const roomsList = document.getElementById('rooms-list');

const roomTitle = document.getElementById('room-title');
const player1Slot = document.getElementById('player-1');
const player2Slot = document.getElementById('player-2');
const addAiBtn = document.getElementById('add-ai-btn');
const startGameBtn = document.getElementById('start-game-btn');
const leaveRoomBtn = document.getElementById('leave-room-btn');

const oppName = document.getElementById('opp-name');
const oppScore = document.getElementById('opp-score');
const oppCollected = document.getElementById('opp-collected');

const fieldCards = document.getElementById('field-cards');

const myCards = document.getElementById('my-cards');
const myCollected = document.getElementById('my-collected');
const myName = document.getElementById('my-name');
const myScore = document.getElementById('my-score');

// Modal
const gameOverModal = document.getElementById('game-over-modal');
const returnToRoomBtn = document.getElementById('return-to-room-btn');
const gameOverBody = document.getElementById('game-over-body');

let mySid = null;
let currentRoomId = null;
let myPlayerIdx = 0;
let gameState = null;

// Categories for Collected
const typeMap = {
    'scene': { name: '景色牌', order: 1 },
    'spot': { name: '地点牌', order: 2 },
    'item': { name: '物品牌', order: 3 },
    'character': { name: '人物牌', order: 4 }
};

// Event Listeners
setNameBtn.addEventListener('click', () => {
    const name = usernameInput.value.trim() || 'Guest';
    socket.emit('set_name', name);
    loginSection.classList.add('hidden');
    roomsSection.classList.remove('hidden');
});
createRoomBtn.addEventListener('click', () => socket.emit('create_room'));
leaveRoomBtn.addEventListener('click', () => {
    socket.emit('leave_room'); 
    location.reload();
});
addAiBtn.addEventListener('click', () => socket.emit('add_ai'));
startGameBtn.addEventListener('click', () => socket.emit('start_game'));
returnToRoomBtn.addEventListener('click', () => {
    gameOverModal.classList.add('hidden');
    socket.emit('escape_game');
});

// Socket Events
socket.on('info', (data) => {
    if(data.sid) mySid = data.sid;
    displayName.textContent = data.name;
});

socket.on('room_created', (data) => {
    currentRoomId = data.room_id;
    lobbyScreen.classList.add('hidden');
    roomScreen.classList.remove('hidden');
    gameScreen.classList.add('hidden');
    roomTitle.textContent = `房间: ${data.room_id}`;
});

socket.on('lobby_update', (rooms) => {
    roomsList.innerHTML = '';
    rooms.forEach(r => {
        let li = document.createElement('li');
        li.style.marginBottom = '10px';
        li.style.display = 'flex';
        li.style.justifyContent = 'space-between';
        li.style.alignItems = 'center';
        li.style.padding = '10px';
        li.style.background = 'rgba(255,255,255,0.05)';
        li.style.borderRadius = '5px';
        
        let info = document.createElement('span');
        info.textContent = `房间 ${r.room_id} (${r.players_count}/2) - ${r.status}`;
        li.appendChild(info);
        
        if(r.players_count < 2 && r.status === 'waiting') {
            let joinBtn = document.createElement('button');
            joinBtn.className = 'btn';
            joinBtn.textContent = '加入';
            joinBtn.onclick = () => socket.emit('join_room', r.room_id);
            li.appendChild(joinBtn);
        }
        roomsList.appendChild(li);
    });
});

setInterval(() => {
    if (!roomsSection.classList.contains('hidden')) {
        socket.emit('get_lobby');
    }
}, 3000);

socket.on('room_update', (data) => {
    if(data.status === 'playing') {
        roomScreen.classList.add('hidden');
        gameScreen.classList.remove('hidden');
        return;
    }
    
    // Back from game
    gameOverModal.classList.add('hidden');
    lobbyScreen.classList.add('hidden');
    gameScreen.classList.add('hidden');
    roomScreen.classList.remove('hidden');
    
    if(data.room_id !== currentRoomId){
         currentRoomId = data.room_id;
         roomTitle.textContent = `房间: ${data.room_id}`;
    }
    
    player1Slot.textContent = data.players[0] ? data.players[0].name : "等待中...";
    player2Slot.textContent = data.players[1] ? data.players[1].name : "等待中...";

    if (data.owner === mySid) {
        if(data.players.length < 2) addAiBtn.classList.remove('hidden');
        else addAiBtn.classList.add('hidden');
        if(data.players.length === 2) startGameBtn.classList.remove('hidden');
        else startGameBtn.classList.add('hidden');
    } else {
        addAiBtn.classList.add('hidden');
        startGameBtn.classList.add('hidden');
    }
});

socket.on('game_state', (state) => {
    gameState = state;
    gameOverModal.classList.add('hidden');
    if(document.getElementById('koikoi-modal')) document.getElementById('koikoi-modal').remove();
    roomScreen.classList.add('hidden');
    lobbyScreen.classList.add('hidden');
    gameScreen.classList.remove('hidden');
    
    myPlayerIdx = state.my_idx;
    renderGame(state);
});

function renderGame(state) {
    // 顶部对手信息
    oppName.innerHTML = `<strong>${state.opp_player.name}</strong>`;
    oppScore.innerHTML = `<div class="info-item">总:${state.opp_player.score}分</div><div class="info-item">局:${state.opp_player.round_score}</div><div class="info-item">得札:${state.opp_player.collected.length}</div>`;
    
    // 渲染对手手牌数
    if (document.getElementById('opp-hand-count')) {
        document.getElementById('opp-hand-count').textContent = state.opp_player.hand_count || 0;
    }
    
    // 对手得札
    renderCollected(state.opp_player.collected, oppCollected);

    // 中间场札
    fieldCards.innerHTML = '';
    state.field.forEach(card => {
        let cardEl = createCardEl(card);
        // Highlight logic when hovering field card
        cardEl.onmouseenter = () => {
            Array.from(myCards.children).forEach((cNode, cIdx) => {
                if(state.my_player.hand[cIdx].card_id === card.card_id) {
                    cNode.classList.add('highlight-match');
                }
            });
        };
        cardEl.onmouseleave = () => {
            Array.from(myCards.children).forEach(cNode => cNode.classList.remove('highlight-match'));
        };
        fieldCards.appendChild(cardEl);
    });

    // 我方得札
    renderCollected(state.my_player.collected, myCollected);

    // 底部我方信息与手牌
    myName.innerHTML = `<strong>${state.my_player.name}</strong>`;
    let turnIndicator = state.current_turn_sid === state.my_player.sid ? `<div class="info-item highlight-turn">(你的回合)</div>` : "";
    myScore.innerHTML = `<div class="info-item">总:${state.my_player.score}分</div><div class="info-item">局:${state.my_player.round_score}</div><div class="info-item">得札:${state.my_player.collected.length}</div>${turnIndicator}`;
    
    myCards.innerHTML = '';
    state.my_player.hand.forEach((card, idx) => {
        let cardEl = createCardEl(card);
        cardEl.style.zIndex = 50 + idx;
        
        if (idx > 0) {
            // compensate for 2px gap to get ~1/3 overlap
            cardEl.style.marginLeft = '-19.6px'; 
        }

        let hoverTimer = null;
        let isSelected = false;

        const setFieldHighlight = (show) => {
            Array.from(fieldCards.children).forEach((fNode, fIdx) => {
                if(state.field[fIdx].card_id === card.card_id) {
                    if (show) fNode.classList.add('highlight-match');
                    else fNode.classList.remove('highlight-match');
                } else {
                    if (show) fNode.classList.add('dimmed');
                    else fNode.classList.remove('dimmed');
                }
            });
        };

        const setTopAndFloat = (show) => {
            if (show) {
                cardEl.style.zIndex = 100;
                cardEl.style.transform = 'translateY(-15px)';
            } else {
                cardEl.style.zIndex = 50 + idx;
                cardEl.style.transform = 'none';
            }
        };

        // Immediately highlight fields on mouse enter
        cardEl.onmouseenter = () => {
            setFieldHighlight(true);
            hoverTimer = setTimeout(() => {
                if (!isSelected) {
                    isSelected = true;
                    setTopAndFloat(true);
                }
            }, 300);
        };
        
        cardEl.onmouseleave = () => {
            if (hoverTimer) clearTimeout(hoverTimer);
            isSelected = false;
            setFieldHighlight(false);
            setTopAndFloat(false);
        };

        if (state.state === 'WAITING_FOR_PLAY' && state.current_turn_sid === state.my_player.sid) {
            cardEl.onclick = () => {
                if (!isSelected) {
                    if (hoverTimer) clearTimeout(hoverTimer);
                    isSelected = true;
                    setFieldHighlight(true);
                    setTopAndFloat(true);
                } else {
                    isSelected = false;
                    setFieldHighlight(false);
                    setTopAndFloat(false);
                    socket.emit('play_card', idx);
                }
            };
        } else {
            cardEl.style.cursor = 'not-allowed';
            cardEl.style.filter = 'brightness(0.7)';
            
            cardEl.onclick = () => {
                if (!isSelected) {
                    if (hoverTimer) clearTimeout(hoverTimer);
                    isSelected = true;
                    setFieldHighlight(true);
                    setTopAndFloat(true);
                } else {
                    isSelected = false;
                    setFieldHighlight(false);
                    setTopAndFloat(false);
                }
            };
        }
        myCards.appendChild(cardEl);
    });
    
    handleSpecialStates(state);
}

function renderCollected(cards, container) {
    container.innerHTML = '';
    // Group by category
    let groups = {};
    cards.forEach(c => {
        if(!groups[c.card_type]) groups[c.card_type] = [];
        groups[c.card_type].push(c);
    });
    
    // Sort keys by typeMap order
    let sortedKeys = Object.keys(groups).sort((a,b) => typeMap[a].order - typeMap[b].order);
    
    sortedKeys.forEach(key => {
        let col = document.createElement('div');
        col.className = 'collected-col';
        
        let title = document.createElement('div');
        title.className = 'col-title';
        title.textContent = `${typeMap[key].name} ${groups[key].length}`;
        col.appendChild(title);
        
        let maxIdx = groups[key].length - 1;
        let numCols = Math.floor(maxIdx / 5) + 1;
        
        let stack = document.createElement('div');
        stack.className = 'col-cards';
        stack.style.width = `${numCols * 55 + 5}px`;
        groups[key].forEach((c, idx) => {
            let wrap = document.createElement('div');
            wrap.className = 'col-card-wrapper';
            wrap.style.top = `${(idx % 5) * 20}px`;
            wrap.style.left = `${Math.floor(idx / 5) * 55}px`;
            wrap.style.zIndex = 100 - idx;
            wrap.appendChild(createCardEl(c));
            stack.appendChild(wrap);
        });
        col.appendChild(stack);
        container.appendChild(col);
    });
}

function handleSpecialStates(state) {
    // If modal was open from last action but now game is over
    if (state.state === 'GAME_OVER') {
        const winner = state.p1.round_score > state.p2.round_score ? state.p1 : (state.p2.round_score > state.p1.round_score ? state.p2 : null);
        
        let title = '流局 (无人得分)';
        let bodyHTML = `<p>本局没有任何一方得分或顺利结算！</p>
                        <p style="color:#d4af37; font-weight:bold; margin-top:10px;">目前累计总分 - ${state.p1.name}: ${state.p1.score} | ${state.p2.name}: ${state.p2.score}</p>`;
        
        if (winner) {
            const loser = winner === state.p1 ? state.p2 : state.p1;
            title = `${winner.name} 赢了本局!`;
            bodyHTML = `
                <h3>${winner.name} 本局获得 ${winner.round_score} 分!</h3>
                <p>达成役种: ${winner.yizhong.join(', ') || '无'}</p>
                <hr style="border-color:#333; margin:10px 0;">
                <p style="color:#aaa">${loser.name}: 0 分得点</p>
                <p style="color:#d4af37; font-weight:bold; margin-top:10px;">累计总分 - ${state.p1.name}: ${state.p1.score} | ${state.p2.name}: ${state.p2.score}</p>
            `;
        }
        document.getElementById('game-over-title').textContent = title;
        gameOverBody.innerHTML = bodyHTML;
        
        let container = document.getElementById('game-over-btn-container');
        if(!container) {
            container = document.createElement('div');
            container.id = 'game-over-btn-container';
            container.style.display = 'flex';
            container.style.gap = '10px';
            returnToRoomBtn.parentNode.appendChild(container);
            returnToRoomBtn.style.display = 'none';
        }
        container.innerHTML = '';
        
        const nextBtn = document.createElement('button');
        nextBtn.className = 'btn success-btn';
        nextBtn.textContent = '直接继续下一局';
        nextBtn.style.flex = '1';
        nextBtn.onclick = () => { 
            nextBtn.textContent = '等待对方...';
            nextBtn.disabled = true;
            socket.emit('agree_next_round'); 
        };
        
        const exitBtn = document.createElement('button');
        exitBtn.className = 'btn danger-btn';
        exitBtn.textContent = '返回大厅清算';
        exitBtn.style.flex = '1';
        exitBtn.onclick = () => {
            gameOverModal.classList.add('hidden');
            socket.emit('escape_game');
        };
        container.appendChild(nextBtn);
        container.appendChild(exitBtn);
        
        gameOverModal.classList.remove('hidden');
        return;
    }

    if (state.current_action_sid === state.my_player.sid) {
        if (state.state === 'WAITING_FOR_MATCH_CHOICE') {
            const matchesDiv = document.createElement('div');
            matchesDiv.id = 'choice-modal';
            matchesDiv.className = 'modal-overlay';
            
            const cont = document.createElement('div');
            cont.className = 'modal-content glass-panel';
            cont.innerHTML = '<h3>有复数配合场札，请选择吃哪一张？</h3>';
            
            const cardsContainer = document.createElement('div');
            cardsContainer.style.display = 'flex';
            cardsContainer.style.justifyContent = 'center';
            cardsContainer.style.gap = '15px';
            cardsContainer.style.marginTop = '20px';
            
            state.pending_matches.forEach((c, idx) => {
                let cardEl = createCardEl(c);
                cardEl.style.transform = "scale(1.5)";
                cardEl.style.margin = "20px";
                cardEl.onclick = () => {
                    socket.emit('choose_match', idx);
                    matchesDiv.remove();
                };
                cardsContainer.appendChild(cardEl);
            });
            cont.appendChild(cardsContainer);
            matchesDiv.appendChild(cont);
            document.body.appendChild(matchesDiv);
        }
        
        if (state.state === 'WAITING_FOR_KOIKOI') {
            // Remove lingering modal just in case
            if(document.getElementById('koikoi-modal')) document.getElementById('koikoi-modal').remove();
            
            const koikoiDiv = document.createElement('div');
            koikoiDiv.id = 'koikoi-modal';
            koikoiDiv.className = 'modal-overlay';
            
            const cont = document.createElement('div');
            cont.className = 'modal-content glass-panel';
            cont.innerHTML = `<h3>新役达成！若此刻结算可获: ${state.my_player.round_score}分</h3><p>${state.my_player.yizhong.join(', ')}</p><p>是否继续游戏(Koi-Koi)？</p>`;
            
            const btnYes = document.createElement('button');
            btnYes.className = 'btn success-btn';
            btnYes.textContent = '继续 (Koi-Koi)';
            btnYes.onclick = () => { socket.emit('choose_koikoi', true); koikoiDiv.remove(); };
            
            const btnNo = document.createElement('button');
            btnNo.className = 'btn danger-btn';
            btnNo.textContent = '结束清算';
            btnNo.onclick = () => { socket.emit('choose_koikoi', false); koikoiDiv.remove(); };
            
            cont.appendChild(btnYes);
            cont.appendChild(btnNo);
            koikoiDiv.appendChild(cont);
            document.body.appendChild(koikoiDiv);
        }
    }
}

function createCardEl(cardObj) {
    const el = document.createElement('div');
    el.className = 'card';
    el.style.backgroundImage = `url('${cardObj.img_url}')`;
    el.title = cardObj.name;
    return el;
}
