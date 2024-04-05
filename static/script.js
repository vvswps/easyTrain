const webcamBtn1 = document.querySelector("#webcam-btn-1");

webcamBtn1.addEventListener("click", function () {
  navigator.mediaDevices
    .getUserMedia({ video: true })
    .then(function (stream) {
      let video = document.querySelector("#preview-1");
      video.srcObject = stream;
      video.play();
    })
    .catch(function (error) {
      console.error("Error accessing webcam:", error);
    });
});

const webcamBtn2 = document.querySelector("#webcam-btn-2");

webcamBtn2.addEventListener("click", function () {
  navigator.mediaDevices
    .getUserMedia({ video: true })
    .then(function (stream) {
      let video = document.querySelector("#preview-2");
      video.srcObject = stream;
      video.play();
    })
    .catch(function (error) {
      console.error("Error accessing webcam:", error);
    });
});
