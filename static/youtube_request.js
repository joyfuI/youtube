"use strict";

const url = document.getElementById('url');
const analysis_btn = document.getElementById('analysis_btn');
const go_btn = document.getElementById('go_btn');
const content_div = document.getElementById('content_div');
const button_div = document.getElementById('button_div');
const detail_div = document.getElementById('detail_div');
const list_div = document.getElementById('list_div');
const youtube_modal_title = document.getElementById('youtube_modal_title');
const modal_type = document.getElementById('modal_type');
const video_urls = document.getElementById('video_urls');
const format = document.getElementById('format');
const convert_mp3 = document.getElementById('convert_mp3');
const youtube_modal_save_btn = document.getElementById('youtube_modal_save_btn');

analysis_btn.addEventListener('click', click_analysis_btn);

go_btn.addEventListener('click', (event) => {
    event.preventDefault();
    if (url.value.startsWith('http')) {
        open(url.value, '_blank');
    }
});

content_div.addEventListener('click', (event) => {
    event.preventDefault();
    const target = event.target;
    if (target.tagName !== 'BUTTON') {
        return;
    }
    const data = target.dataset;
    if (target.classList.contains('youtube-download')) {
        // 다운로드 추가
        youtube_modal_title.textContent = '다운로드 추가';
        modal_type.value = '0';
        video_urls.value = data.url;
        $('#youtube_modal').modal();
    } else if (target.classList.contains('youtube-request')) {
        // 요청
        url.value = data.url;
        click_analysis_btn(event);
    }
});

button_div.addEventListener('click', (event) => {
    event.preventDefault();
    const target = event.target;
    if (target.tagName !== 'BUTTON') {
        return;
    }
    switch (target.id) {
        // 선택 다운로드 추가
        case 'check_download_btn':
            let urls = '';
            for (const item of document.querySelectorAll('#list_div input.youtube-list')) {
                if (item.checked) {
                    urls += `${item.dataset.url}\n`;
                }
            }
            urls = urls.slice(0, -1);
            if (urls.length === 0) {
                notify('다운로드할 영상을 선택하세요.', 'warning');
            } else {
                youtube_modal_title.textContent = '선택 다운로드 추가';
                modal_type.value = '0';
                video_urls.value = urls;
                $('#youtube_modal').modal();
            }
            break;

        // 전체 선택
        case 'all_check_on_btn':
            $('#list_div input.youtube-list').bootstrapToggle('on');
            break;

        // 전체 해제
        case 'all_check_off_btn':
            $('#list_div input.youtube-list').bootstrapToggle('off');
            break;

        // 스케줄러에 추가
        case 'add_scheduler_btn':
            youtube_modal_title.textContent = '스케줄러에 추가';
            modal_type.value = '1';
            video_urls.value = target.dataset.url;
            $('#youtube_modal').modal();
            break;
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

// 모달 추가 버튼
youtube_modal_save_btn.addEventListener('click', (event) => {
    event.preventDefault();
    const type = parseInt(modal_type.value);
    const form_data = new URLSearchParams(get_formdata('#modal_form'));
    if (type === 0) {
        // 다운로드 추가
        video_urls.value.split('\n').forEach((url) => form_data.append('download[]', url));
        fetch(`/${package_name}/ajax/add_download`, {
            method: 'POST',
            cache: 'no-cache',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
            },
            body: form_data
        }).then(response => response.json()).then((data) => {
            notify(`${data}개를 큐에 추가하였습니다.`, 'success');
        }).catch(() => {
            notify('실패하였습니다.', 'danger');
        });
    } else if (type === 1) {
        // 스케줄러 추가
        form_data.append('url', video_urls.value);
        fetch(`/${package_name}/ajax/add_scheduler`, {
            method: 'POST',
            cache: 'no-cache',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
            },
            body: form_data
        }).then(response => response.json()).then(() => {
            notify('스케줄을 저장하였습니다.', 'success');
        }).catch(() => {
            notify('실패하였습니다.', 'danger');
        });
    }
    $('#youtube_modal').modal('hide');
});

function click_analysis_btn(event) {
    event.preventDefault();
    if (!url.value.startsWith('http')) {
        notify('URL을 입력하세요.', 'warning');
        return;
    }
    fetch(`/${package_name}/ajax/analysis`, {
        method: 'POST',
        cache: 'no-cache',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8'
        },
        body: new URLSearchParams({
            url: url.value
        })
    }).then(response => response.json()).then((data) => {
        if (data.errorCode !== 0) {
            notify('분석 실패', 'warning');
            return;
        }
        button_div.innerHTML = '';
        detail_div.innerHTML = '';
        list_div.innerHTML = '';
        const info_dict = data.info_dict;
        const type = check_type(info_dict);
        if (type === 'playlist') {
            // 플레이리스트 주소
            button_div.innerHTML = make_button_scheduler(info_dict.webpage_url);
            detail_div.innerHTML = make_info(info_dict);
            let str = '';
            let index = 0;
            for (const entry of info_dict.entries) {
                if (info_dict.extractor_key === 'YoutubeTab') {
                    str += make_item_youtube(entry, ++index);
                } else {
                    str += make_item(entry, ++index);
                }
            }
            list_div.innerHTML = str;
            $('input.youtube-list').bootstrapToggle();
        } else if (type === 'video') {
            // 동영상 주소
            button_div.innerHTML = make_button_download(info_dict.webpage_url);
            detail_div.innerHTML = make_info(info_dict);
        } else if (type === 'channel') {
            // 유튜브 채널 주소
            detail_div.innerHTML = make_info(info_dict);
            let str = '';
            let index = 0;
            for (const entry of info_dict.entries) {
                str += make_item_channel(entry, ++index);
            }
            list_div.innerHTML = str;
        }
    }).catch(() => {
        notify('요청 실패', 'danger');
    });
}

function check_type(info_dict) {
    if (info_dict._type === 'playlist') {
        if (info_dict.extractor_key === 'YoutubeTab' && info_dict.entries.length > 0 && info_dict.entries[0].ie_key === null) {
            return 'channel';
        } else {
            return 'playlist';
        }
    } else {
        return 'video';
    }
}

function make_button_download(url) {
    return `<button class="btn btn-sm btn-outline-success youtube-download" data-url="${url}">다운로드 추가</button>`;
}

function make_button_scheduler(url) {
    let str = m_button('check_download_btn', '선택 다운로드 추가');
    str += m_button('all_check_on_btn', '전체 선택');
    str += m_button('all_check_off_btn', '전체 해제');
    str += m_button('add_scheduler_btn', '스케줄러에 추가', [{key: 'url', value: url}]);
    return m_button_group(str);
}

function make_info(data) {
    let str = m_hr_black();
    str += m_row_start(0);
    // 썸네일
    if (data.thumbnail) {
        str += m_col(3, `<img class="img-fluid" src="${data.thumbnail}" alt="${data.title}">`);
    }
    // 정보
    let tmp = '';
    if (data.webpage_url) {
        tmp += make_col('제목', `<a href="${data.webpage_url}" target="_blank">${data.title}</a>`);
    } else {
        tmp += make_col('제목', data.title);
    }
    if (data.uploader) {
        if (data.uploader_url) {
            tmp += make_col('업로더', `<a href="${data.uploader_url}" target="_blank">${data.uploader}</a>`);
        } else {
            tmp += make_col('업로더', data.uploader);
        }
    }
    if (data.upload_date) {
        const date = data.upload_date;
        tmp += make_col('날짜', `${date.substr(0, 4)}. ${date.substr(4, 2)}. ${date.substr(6, 2)}.`);
    }
    if (data.view_count) {
        tmp += make_col('조회수', `${data.view_count.toLocaleString()}회`);
    }
    if (data.description) {
        tmp += make_col('설명', convert_description(data.description));
    }
    if (data.duration) {
        tmp += make_col('길이', convert_duration(data.duration));
    }
    if (data.width && data.height) {
        let tmp2 = `${data.width}x${data.height}`;
        if (data.fps) {
            tmp2 += `@${data.fps}`;
        }
        tmp += make_col('화질', tmp2);
    }
    if (data.entries) {
        tmp += make_col('동영상 수', `${data.entries.length}개`);
    }
    str += m_col(9, tmp);

    str += m_row_end();
    str += m_hr_black();
    return str;
}

function make_item(data, index) {
    let str = m_row_start(0);
    str += m_col(1, index);
    if (data.thumbnail) {
        str += m_col(2, `<img class="img-fluid" src="${data.thumbnail}" alt="${data.title}">`);
    } else {
        str += m_col(2, '');
    }
    str += m_col(6, `<a href="${data.url}" target="_blank">${data.title}</a>`);

    let tmp = '<div class="form-inline">';
    tmp += `<input class="youtube-list" type="checkbox" data-toggle="toggle" data-on="선 택" data-off="-" data-onstyle="success" data-offstyle="danger" data-size="small" data-url="${data.url}" checked>&nbsp;&nbsp;&nbsp;&nbsp;`;
    tmp += make_button_download(data.url);
    tmp += '</div>';
    str += m_col(3, tmp, 'right');

    str += m_row_end();
    str += m_hr(0);
    return str;
}

function make_item_youtube(data, index) {
    let str = m_row_start(0);
    str += m_col(1, index);
    str += m_col(2, `<img class="img-fluid" src="https://i.ytimg.com/vi/${data.id}/hqdefault.jpg" alt="${data.title}">`);
    str += m_col(6, `<a href="https://www.youtube.com/watch?v=${data.url}" target="_blank">${data.title}</a>`);

    let tmp = '<div class="form-inline">';
    tmp += `<input class="youtube-list" type="checkbox" data-toggle="toggle" data-on="선 택" data-off="-" data-onstyle="success" data-offstyle="danger" data-size="small" data-url="https://www.youtube.com/watch?v=${data.url}" checked>&nbsp;&nbsp;&nbsp;&nbsp;`;
    tmp += make_button_download(`https://www.youtube.com/watch?v=${data.url}`);
    tmp += '</div>';
    str += m_col(3, tmp, 'right');

    str += m_row_end();
    str += m_hr(0);
    return str;
}

function make_item_channel(data, index) {
    let str = m_row_start(0);
    str += m_col(1, index);
    str += m_col(8, `<a href="${data.url}" target="_blank">${data.title}</a>`);

    let tmp = `<button class="btn btn-sm btn-outline-success youtube-request" data-url="${data.url}">분석</button>`;
    str += m_col(3, tmp, 'right');

    str += m_row_end();
    str += m_hr(0);
    return str;
}

function make_col(right, left) {
    let str = m_row_start(0);
    str += m_col(3, `<div class="my-1 font-weight-bold">${right}</div>`, 'right');
    str += m_col(9, `<div class="my-1">${left}</div>`);
    str += m_row_end();
    return str;
}

function convert_description(str) {
    str = str.replace(/#([^\s#]+)/ug, '<a href="https://www.youtube.com/hashtag/$1" target="_blank">#$1</a>');
    str = str.replace(/\n/ug, '<br>');
    return str;
}

function convert_duration(int) {
    let str = '';
    const h = Math.floor(int / 3600);
    const m = Math.floor((int % 3600) / 60);
    const s = int % 60;
    if (h !== 0) {
        str += `${h}:`;
        str += (m < 10) ? `0${m}` : m;
    } else {
        str += m;
    }
    str += (s < 10) ? `:0${s}` : `:${s}`;
    return str;
}
