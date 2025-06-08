const typoSuggestionsContainer = document.getElementById('typo-suggestions-container');
const typoSuggestionsList = document.getElementById('typo-suggestions-list');
const input = document.getElementById('autocomplete-input');
const autocompleteSuggestions = document.querySelector('.suggestions');
const suggestionsList = document.getElementById('suggestions-list');

let isMouseDown = false;
let isDragging = false;

// 선택된 단어를 얻는 함수
function getSelectedWord(inputElem) {
    const start = inputElem.selectionStart;
    const end = inputElem.selectionEnd;
    if (start === end) return null;

    const value = inputElem.value;
    const selectedText = value.substring(start, end).trim();

    if (selectedText.includes(' ') || !selectedText) return null;

    return { selectedText, start, end };
}

// 오타 교정 추천 요청 함수
async function fetchTypoCorrections(word) {
    try {
        const url = `/typo_correction?word=${encodeURIComponent(word)}&max_cost=2&top_k=20&weight_cost=1&weight_freq=0.1&min_freq=1000000`;
        const res = await fetch(url);
        if (!res.ok) throw new Error('Network error');
        return await res.json();
    } catch (e) {
        console.error('Typo correction fetch failed:', e);
        return [];
    }
}

// 오타 추천 UI 표시 함수
function showTypoSuggestions(corrections, inputElem, start, end) {
    typoSuggestionsList.innerHTML = '';

    if (!corrections.length) {
        typoSuggestionsContainer.style.display = 'none';
        return;
    }

    corrections.forEach(correction => {
        const li = document.createElement('li');
        li.textContent = correction.word;
        li.style.cursor = 'pointer';
        li.style.padding = '4px 8px';
        li.style.borderBottom = '1px solid #ddd';

        li.addEventListener('click', () => {
            const val = inputElem.value;
            inputElem.value = val.slice(0, start) + correction.word + val.slice(end);
            inputElem.focus();
            const cursorPos = start + correction.word.length;
            inputElem.setSelectionRange(cursorPos, cursorPos);

            typoSuggestionsContainer.style.display = 'none';
            typoSuggestionsList.innerHTML = '';
        });

        typoSuggestionsList.appendChild(li);
    });

}

// 자동완성 실행 함수
async function triggerAutocomplete(prefix) {
    if (!prefix) {
        autocompleteSuggestions.style.display = 'none';
        autocompleteSuggestions.innerHTML = '';
        return;
    }

    try {
        const res = await fetch(`/autocomplete?prefix=${encodeURIComponent(prefix)}&top_k=20`);
        if (!res.ok) throw new Error('Autocomplete error');
        const data = await res.json();

        autocompleteSuggestions.innerHTML = '';
        if (data.length === 0) {
            autocompleteSuggestions.style.display = 'none';
            return;
        }

        data.forEach(([word, freq]) => {
            const li = document.createElement('li');
            li.textContent = word;
            li.style.cursor = 'pointer';
            li.style.padding = '4px 8px';
            li.style.borderBottom = '1px solid #eee';

            li.addEventListener('click', () => {
                input.value = word;
                autocompleteSuggestions.style.display = 'none';
                autocompleteSuggestions.innerHTML = '';
                input.focus();
            });

            autocompleteSuggestions.appendChild(li);
        });

    } catch (err) {
        console.error(err);
        autocompleteSuggestions.style.display = 'none';
        autocompleteSuggestions.innerHTML = '';
    }
}

// 입력창에 드래그 후 오타 추천 표시
input.addEventListener('mouseup', async () => {
    isMouseDown = false;

    // 드래그가 끝나고 나서 선택된 단어가 있으면 오타 추천 요청
    const selection = getSelectedWord(input);
    if (selection) {
        const corrections = await fetchTypoCorrections(selection.selectedText);
        showTypoSuggestions(corrections, input, selection.start, selection.end);
    } else {
        // 선택 없으면 오타 추천 숨기기
        typoSuggestionsContainer.style.display = 'none';
        typoSuggestionsList.innerHTML = '';
    }
});

// 키보드 방향키/ESC 입력 시 오타 추천 숨김
input.addEventListener('keyup', e => {
    if (['ArrowLeft', 'ArrowRight', 'Escape'].includes(e.key)) {
        typoSuggestionsContainer.style.display = 'none';
        typoSuggestionsList.innerHTML = '';
    }
});


input.addEventListener('mousedown', () => {
    isMouseDown = true;
    isDragging = false;

    // 자동완성 목록 둘 다 숨기기 + 비우기
    autocompleteSuggestions.innerHTML = '';
    autocompleteSuggestions.style.display = 'none';

    if (suggestionsList) {
        suggestionsList.innerHTML = '';
        suggestionsList.style.display = 'none';
    }
});

input.addEventListener('mousemove', () => {
    if (isMouseDown) {
        isDragging = true;

        autocompleteSuggestions.innerHTML = '';
        autocompleteSuggestions.style.display = 'none';

        if (suggestionsList) {
            suggestionsList.innerHTML = '';
            suggestionsList.style.display = 'none';
        }
    }
});

// 드래그 종료 처리
document.addEventListener('mouseup', () => {
    isMouseDown = false;
    // 마우스가 올라왔을 때 이벤트에서 선택된 텍스트 처리하므로 여기선 따로 안 함
});
