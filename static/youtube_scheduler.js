"use strict";

const add_btn = document.getElementById('add_btn');
const list_div = document.getElementById('list_div');
const modal_form = document.getElementById('modal_form');
const db_id = document.getElementById('db_id');
const url = document.getElementById('url');
const save_path = document.getElementById('save_path');
const filename = document.getElementById('filename');
const format = document.getElementById('format');
const convert_mp3 = document.getElementById('convert_mp3');
const date_after = document.getElementById('date_after');
const schedule_modal_save_btn = document.getElementById('schedule_modal_save_btn');
const confirm_title = document.getElementById('confirm_title');
const confirm_body = document.getElementById('confirm_body');

let current_data;

// 리스트 로딩
fetch(`/${package_name}/ajax/list_scheduler`, {
    method: 'POST',
    cache: 'no-cache',
    headers: {
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
    }
}).then(response => response.json()).then(make_list);

// 스케줄 추가
add_btn.addEventListener('click', (event) => {
    event.preventDefault();
    db_id.value = '';
    url.disabled = false;
    modal_form.reset();
    $('#convert_mp3').bootstrapToggle('off');
    $('#daterange').bootstrapToggle('off');
    $('#playlistreverse').bootstrapToggle('off');
    $('#schedule_modal').modal();
});

list_div.addEventListener('click', (event) => {
    event.preventDefault();
    const target = event.target;
    if (target.tagName !== 'BUTTON') {
        return;
    }
    const index = target.dataset.id;
    if (target.classList.contains('youtube-edit')) {
        // 스케줄 수정
        db_id.value = index;
        url.value = current_data[index].url;
        url.disabled = true;
        save_path.value = current_data[index].save_path;
        filename.value = current_data[index].filename;
        format.value = current_data[index].format;
        $('#convert_mp3').bootstrapToggle((current_data[index].convert_mp3) ? "on" : "off");
        $('#daterange').bootstrapToggle((current_data[index].date_after) ? "on" : "off");
        $('#playlistreverse').bootstrapToggle((current_data[index].playlistreverse) ? "on" : "off");
        let date_after_data = current_data[index].date_after;
        if (date_after_data) {
            date_after_data = new Date(date_after_data);
            const year = date_after_data.getFullYear().toString().padStart(4, '0');
            const month = (date_after_data.getMonth() + 1).toString().padStart(2, '0');
            const date = date_after_data.getDate().toString().padStart(2, '0');
            date_after_data = `${year}-${month}-${date}`;
            date_after.value = date_after_data;
        }
        $('#schedule_modal').modal();
    } else if (target.classList.contains('youtube-del')) {
        // 스케줄 삭제
        confirm_title.textContent = '스케줄 삭제';
        confirm_body.textContent = '해당 스케줄을 삭제하시겠습니까?';
        $('#confirm_button').off('click').click(index, del_scheduler);
        $('#confirm_modal').modal();
    } else if (target.classList.contains('youtube-archive')) {
        // Archive 삭제
        confirm_title.textContent = 'Archive 삭제';
        confirm_body.innerHTML = 'Archive 파일을 삭제하시겠습니까?<br>Archive 파일은 중복 다운로드를 막기 위해 이미 다운로드한 동영상 정보를 기록한 파일입니다. 삭제 시 플레이리스트 전체를 처음부터 다운로드합니다.';
        $('#confirm_button').off('click').click(index, del_archive);
        $('#confirm_modal').modal();
    }
});

// mp3 변환
$('#convert_mp3').change(() => {
    if (convert_mp3.checked) {
        format.value = 'bestaudio/best';
    }
});

// 날짜 지정
$('#daterange').change(() => {
    use_collapse('daterange');
});

// 스케줄 저장
schedule_modal_save_btn.addEventListener('click', (event) => {
    event.preventDefault();
    $('#schedule_modal').modal('hide');
    if (!url.value.startsWith('http')) {
        notify('URL을 입력하세요.', 'warning');
        return;
    }
    fetch(`/${package_name}/ajax/add_scheduler`, {
        method: 'POST',
        cache: 'no-cache',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        },
        body: get_formdata('#modal_form')
    }).then(response => response.json()).then((data) => {
        if (data === null) {
            notify('플레이리스트가 아닙니다.', 'warning');
            return;
        }
        make_list(data);
        notify('스케줄을 저장하였습니다.', 'success');
    }).catch(() => {
        notify('실패하였습니다.', 'danger');
    });
});

function make_list(data) {
    current_data = {};
    let str = '';
    for (const item of data) {
        current_data[item.id] = item;
        str += make_item(item);
    }
    list_div.innerHTML = str;
}

function make_item(data) {
    let str = m_row_start();
    let tmp = `<strong><a href="${data.url}" target="_blank">${data.title}</a></strong><br><br>`;
    tmp += `<a href="${data.uploader_url}" target="_blank">${data.uploader}</a>`;
    str += m_col(4, tmp);

    tmp = m_row_start(0);
    tmp += m_col2(3, '저장 경로', 'right');
    tmp += m_col2(9, data.path);
    tmp += m_row_end();
    tmp += m_row_start(0);
    tmp += m_col2(3, '동영상 포맷', 'right');
    tmp += m_col2(9, data.format);
    tmp += m_row_end();
    tmp += m_row_start(0);
    tmp += m_col2(3, 'mp3로 변환', 'right');
    tmp += m_col2(9, (data.convert_mp3) ? '사용' : '사용안함');
    tmp += m_row_end();
    str += m_col(4, tmp);

    tmp = `동영상 개수: ${data.count}<br>`;
    tmp += `마지막 실행: ${data.last_time}<br><br>`;
    let tmp2 = `<button class="btn btn-sm btn-outline-success youtube-edit" data-id="${data.id}">스케줄 수정</button>`;
    tmp2 += `<button class="btn btn-sm btn-outline-success youtube-del" data-id="${data.id}">스케줄 삭제</button>`;
    tmp2 += `<button class="btn btn-sm btn-outline-success youtube-archive" data-id="${data.id}">Archive 삭제</button>`;
    tmp += m_button_group(tmp2);
    str += m_col(4, tmp);

    str += m_row_end();
    str += m_hr(0);
    return str;
}

// 스케줄 삭제
function del_scheduler(event) {
    event.preventDefault();
    fetch(`/${package_name}/ajax/del_scheduler`, {
        method: 'POST',
        cache: 'no-cache',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        },
        body: new URLSearchParams({
            id: event.data
        })
    }).then(response => response.json()).then((data) => {
        make_list(data);
        notify('삭제하였습니다.', 'success');
    }).catch(() => {
        notify('실패하였습니다.', 'danger');
    });
}

// Archive 삭제
function del_archive(event) {
    event.preventDefault();
    fetch(`/${package_name}/ajax/del_archive`, {
        method: 'POST',
        cache: 'no-cache',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        },
        body: new URLSearchParams({
            id: event.data
        })
    }).then(response => response.json()).then((data) => {
        make_list(data);
        notify('삭제하였습니다.', 'success');
    }).catch(() => {
        notify('실패하였습니다.', 'danger');
    });
}
