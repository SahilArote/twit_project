
function previewImage(event) {
  const reader = new FileReader();
  reader.onload = function () {
    document.getElementById('imagePreview').src = reader.result;
  };
  reader.readAsDataURL(event.target.files[0]);
}

function autoResize(textarea) {
  textarea.style.height = 'auto';
  textarea.style.height = textarea.scrollHeight + 'px';
}
