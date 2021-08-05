"use strict";

const default_save_path = document.getElementById('default_save_path');
const default_save_path_btn = document.getElementById('default_save_path_btn');
const cookiefile_path = document.getElementById('cookiefile_path');
const cookiefile_path_btn = document.getElementById('cookiefile_path_btn');

// 기본 저장 폴더 경로 선택
default_save_path_btn.addEventListener('click', (event) => {
    event.preventDefault();
    m_select_local_file_modal("저장 경로 선택", default_save_path.value, true, (result) => {
        default_save_path.value = result;
    });
});

// cookiefile 파일 선택
cookiefile_path_btn.addEventListener('click', (event) => {
    event.preventDefault();
    m_select_local_file_modal('파일 선택', path_data, false, (result) => {
        cookiefile_path.value = result;
    });
});
