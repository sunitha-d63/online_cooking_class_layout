document.addEventListener("DOMContentLoaded", function () {
  const playButton = document.getElementById("playButton");
  const video = document.getElementById("recipeVideo");

  playButton.addEventListener("click", function () {
    video.classList.remove("d-none");
    playButton.classList.add("d-none");
    video.play();
  });

  video.addEventListener("ended", function () {
    video.classList.add("d-none");
    playButton.classList.remove("d-none");
  });
});
