/*
If not stated otherwise in this file or this component's LICENSE file the
following copyright and licenses apply:

Copyright 2026 RDK Management

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
*/

// contact.js - wires up the floating "Contact us" widget (partials/contact.html).
// Submits via formsubmit.co so no backend is needed on this static site,
// mirroring the RDK-B Core Broadband contact widget.
(function () {
  var CONTACT_EMAIL = "support@rdkcentral.com";

  var toggle = document.getElementById("contact-toggle");
  var panel = document.getElementById("contact-panel");
  var closeBtn = document.getElementById("contact-close");
  var form = document.getElementById("contact-form");
  var submitBtn = document.getElementById("contact-submit");
  var status = document.getElementById("contact-status");

  if (!toggle || !panel || !form) return;

  toggle.addEventListener("click", function () {
    panel.classList.toggle("open");
    if (panel.classList.contains("open")) {
      document.getElementById("contact-name").focus();
    }
  });
  closeBtn.addEventListener("click", function () {
    panel.classList.remove("open");
  });

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    submitBtn.disabled = true;
    submitBtn.textContent = "Sending…";
    status.textContent = "";
    status.className = "contact-status";

    var payload = {
      name: document.getElementById("contact-name").value,
      email: document.getElementById("contact-email").value,
      message: document.getElementById("contact-message").value,
      _subject: "New message from RDK-V Core Video site",
    };

    fetch("https://formsubmit.co/ajax/" + CONTACT_EMAIL, {
      method: "POST",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body: JSON.stringify(payload),
    })
      .then(function (res) {
        if (!res.ok) throw new Error("HTTP " + res.status);
        return res.json();
      })
      .then(function (data) {
        // formsubmit.co can return HTTP 200 with a JSON body reporting
        // success:false (e.g. when run from a file:// page, or before the
        // destination address has completed its one-time activation).
        if (data && (data.success === false || data.success === "false")) {
          throw new Error(data.message || "submission rejected");
        }
        status.textContent = "Sent — thanks! We'll get back to you.";
        status.className = "contact-status ok";
        form.reset();
      })
      .catch(function (err) {
        status.textContent = "Could not send (" + err.message + "). Try the email link below instead.";
        status.className = "contact-status err";
      })
      .finally(function () {
        submitBtn.disabled = false;
        submitBtn.textContent = "Send";
      });
  });
})();
