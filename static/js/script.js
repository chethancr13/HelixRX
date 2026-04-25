// ✅ Firebase imports (MODULAR VERSION)
import { initializeApp } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-app.js";
import { getStorage, ref, uploadBytes } from "https://www.gstatic.com/firebasejs/10.7.1/firebase-storage.js";

// ✅ Your Firebase config
const firebaseConfig = {
  apiKey: "AIzaSyCC6RzT8xPZvzrfy8sbiJGr720Q62o9SZw",
  authDomain: "helixrx-bff6c.firebaseapp.com",
  projectId: "helixrx-bff6c",
  storageBucket: "helixrx-bff6c.firebasestorage.app",
  messagingSenderId: "295925838553",
  appId: "1:295925838553:web:32d7a0ae830d17718384c8"
};

// ✅ Initialize Firebase
const app = initializeApp(firebaseConfig);
const storage = getStorage(app);

// ✅ Upload Function
window.uploadVCF = async function () {
  const fileInput = document.getElementById("vcfFile");
  const status = document.getElementById("status");

  const file = fileInput.files[0];

  if (!file) {
    status.innerText = "❌ Please select a file";
    return;
  }

  // 🔒 Validate file type
  if (!file.name.endsWith(".vcf")) {
    status.innerText = "❌ Only .vcf files allowed";
    return;
  }

  // 🔒 Validate file size (5MB)
  if (file.size > 5 * 1024 * 1024) {
    status.innerText = "❌ File too large (max 5MB)";
    return;
  }

  try {
    status.innerText = "Uploading...";

    const userId = "user123"; // temp (we'll fix later)
    const storageRef = ref(storage, `vcf/${userId}/${file.name}`);

    await uploadBytes(storageRef, file);

    status.innerText = "✅ Upload successful!";
    console.log("File uploaded");

  } catch (error) {
    console.error(error);
    status.innerText = "❌ Upload failed";
  }
};