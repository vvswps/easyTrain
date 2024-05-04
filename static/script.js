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

// Handle dropdown

const dropdownBtns = document.querySelectorAll(".upload-dropdown-btn");
document.querySelector(".dropdown-content");

dropdownBtns.forEach((btn) => {
  // select the next sibling of the button
  const dropdownContent = btn.nextElementSibling;

  btn.addEventListener("click", function () {
    dropdownContent.classList.toggle("show");
  });
});

// Close the dropdown menu if the user clicks close button in the dropdown
const closeBtns = document.querySelectorAll(".dropdown-close-btn");
closeBtns.forEach((btn) => {
  btn.addEventListener("click", function () {
    const dropdownContent = btn.closest(".dropdown-content");
    dropdownContent.classList.remove("show");
  });
});

// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
// Handle upload image

function handleImageUpload(fileList, className, cardRef) {
  const zip = new JSZip();

  // Add each image to a zip
  for (let i = 0; i < fileList.length; i++) {
    const file = fileList[i];
    zip.file(file.name, file);
  }

  // Generate the zip file asynchronously
  zip.generateAsync({ type: "blob" }).then(
    function (zipFile) {
      // Prepare to send zip file
      const formData = new FormData();
      formData.append("zip", zipFile, className + ".zip"); // Set a filename for the zip
      formData.append("className", className);

      sendImagesToBackend(formData, cardRef);
    },
    function (err) {
      console.error("Error generating zip file:", err);
    }
  );
}

function sendImagesToBackend(data, cardRef) {
  const uploadStatus = cardRef.querySelector(".upload-status");
  fetch("/upload_images", {
    method: "POST",
    body: data,
  })
    .then((response) => {
      if (response.ok) {
        uploadStatus.textContent = "Images uploaded successfully!!!";
        return response.json();
      }
      uploadStatus.textContent = "Error uploading images";
      uploadStatus.style.color = "red";
      throw new Error("Error uploading images");
    })
    .catch((error) => console.error("Error uploading:", error));
}

// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
// Handle upload button click

document.addEventListener("click", (event) => {
  const clickedElement = event.target;

  if (clickedElement.matches(".upload-btn")) {
    const card = clickedElement.closest(".card");
    const imageInput = card.querySelector(
      'input[type="file"][accept="image/*"]'
    );
    const className = card.querySelector(".class-name input").value;
    const uploadStatus = card.querySelector(".upload-status");

    if (imageInput.files.length > 0) {
      uploadStatus.textContent = "Uploading images...";
      const imagePreview = card.querySelector(".image-preview");
      imagePreview.src = URL.createObjectURL(imageInput.files[0]);
      handleImageUpload(imageInput.files, className, card);
    } else {
      uploadStatus.textContent = "No images selected";
      uploadStatus.style.color = "red";
    }
  }
});

// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
// Handle test model click

const testImageInput = document.querySelector("#test-image-upload");
const imagePreview = document.querySelector("#test-image-preview");
const testResult = document.querySelector("#prediction");

function displayError(message) {
  console.error(message);
  testResult.textContent = message;
  testResult.style.color = "red";
}

function displayResult(result) {
  testResult.textContent = result;
  testResult.style.color = "black";
}

document
  .querySelector("#test-model-btn")
  .addEventListener("click", function () {
    const testImage = testImageInput.files[0];

    if (!testImage) {
      displayError("No image selected");
      return;
    }

    imagePreview.src = URL.createObjectURL(testImage);

    const formData = new FormData();
    formData.append("image", testImage);

    fetch("/predict", {
      method: "POST",
      body: formData,
    })
      .then((response) => {
        if (!response.ok) {
          throw new Error("Error testing model");
        }
        return response.json();
      })
      .then((data) => displayResult(data.prediction))
      .catch((error) => displayError(error.message));
  });

// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
// Handle train click
document
  .querySelector("#train-model-btn")
  .addEventListener("click", function () {
    const classNames = Array.from(
      document.querySelectorAll(".class-name input")
    ).map((input) => input.value);
    const trainStatus = document.querySelector("#training-status p");

    trainStatus.textContent = "Training model...";

    fetch("/train", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ classNames: classNames }),
    }).then((response) => {
      if (response.ok) {
        document.querySelector("#model-test-download").style.display = "block";
      } else {
        trainStatus.textContent = "Error training model";
        trainStatus.style.color = "red";
      }
    });
  });

// ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
// Handle download model click
document
  .querySelector("#model-test-download")
  .addEventListener("click", function () {
    fetch("/download_model", {
      method: "GET",
    }).then((response) => {
      if (response.ok) {
        response.blob().then((blob) => {
          const url = URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          a.download = "model.keras";
          a.click();
        });
      } else {
        response.text().then((text) => {
          console.error("Error downloading model:", text);
        });
      }
    });
  });
