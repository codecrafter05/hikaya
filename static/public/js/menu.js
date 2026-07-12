(function () {
  "use strict";

  var MENU_DATA = {};
  var cart = [];
  var lang = localStorage.getItem("hikaya_lang") || "ar";
  var cartPanelOpen = false;
  var addModalOpen = false;
  var cartAnimMs = 280;
  var modalAnimMs = 280;

  var modalItem = null;
  var modalTier = null;
  var modalOptions = [];
  var modalQty = 1;

  var els = {
    root: document.documentElement,
    menuRoot: document.getElementById("menuRoot"),
    categoryNav: document.getElementById("categoryNav"),
    langToggle: document.getElementById("langToggle"),
    cartFab: document.getElementById("cartFab"),
    cartBadge: document.getElementById("cartBadge"),
    cartOverlay: document.getElementById("cartOverlay"),
    cartPanel: document.getElementById("cartPanel"),
    cartLines: document.getElementById("cartLines"),
    cartTotal: document.getElementById("cartTotal"),
    checkoutBtn: document.getElementById("checkoutBtn"),
    closeCart: document.getElementById("closeCart"),
    cartTitle: document.getElementById("cartTitle"),
    totalLabel: document.getElementById("totalLabel"),
    addOverlay: document.getElementById("addOverlay"),
    addModal: document.getElementById("addModal"),
    addModalTitle: document.getElementById("addModalTitle"),
    addModalBody: document.getElementById("addModalBody"),
    addModalTotal: document.getElementById("addModalTotal"),
    addTotalLabel: document.getElementById("addTotalLabel"),
    addConfirmBtn: document.getElementById("addConfirmBtn"),
    closeAdd: document.getElementById("closeAdd"),
    addQtyDec: document.getElementById("addQtyDec"),
    addQtyInc: document.getElementById("addQtyInc"),
    addQtyValue: document.getElementById("addQtyValue"),
  };

  var STR = {
    ar: {
      add: "+ إضافة",
      noImage: "لا توجد صورة",
      emptyMenu: "لا توجد عناصر متاحة حالياً.",
      cart: "سلة الطلب",
      emptyCart: "سلتك فارغة.",
      total: "الإجمالي",
      checkout: "إتمام الطلب",
      orderTitle: "🧾 طلب جديد",
      remove: "حذف",
      langBtn: "EN",
      fromPrice: "يبدأ من",
      addToCart: "إضافة إلى السلة",
      close: "إغلاق",
      quantity: "الكمية",
    },
    en: {
      add: "+ Add",
      noImage: "No image",
      emptyMenu: "No items available right now.",
      cart: "Your Cart",
      emptyCart: "Your cart is empty.",
      total: "Total",
      checkout: "Complete order",
      orderTitle: "🧾 New Order",
      remove: "Remove",
      langBtn: "AR",
      fromPrice: "From",
      addToCart: "Add to cart",
      close: "Close",
      quantity: "Quantity",
    },
  };

  function t(key) {
    return STR[lang][key] || key;
  }

  function readMenuData() {
    var node = document.getElementById("menu-data");
    MENU_DATA = JSON.parse(node.textContent);
  }

  function loadCart() {
    try {
      cart = JSON.parse(localStorage.getItem("hikaya_cart") || "[]");
    } catch (e) {
      cart = [];
    }
  }

  function saveCart() {
    localStorage.setItem("hikaya_cart", JSON.stringify(cart));
  }

  function tierKey(itemId, tier) {
    return itemId + ":" + tier.label_ar + ":" + tier.label_en + ":" + tier.price;
  }

  function choiceKey(choice) {
    return choice.label_ar + ":" + choice.label_en + ":" + Number(choice.price_delta || 0);
  }

  function formatPrice(value) {
    return Number(value).toFixed(3);
  }

  function currency() {
    return MENU_DATA.currency_label || "BHD";
  }

  function localizedName(obj) {
    return lang === "ar" ? obj.name_ar : obj.name_en;
  }

  function localizedNote(obj) {
    return lang === "ar" ? obj.note_ar : obj.note_en;
  }

  function localizedTier(tier) {
    return lang === "ar" ? tier.label_ar : tier.label_en;
  }

  function localizedGroup(group) {
    return lang === "ar" ? group.group_ar : group.group_en;
  }

  function localizedChoice(choice) {
    return lang === "ar" ? choice.label_ar : choice.label_en;
  }

  function itemOptionGroups(item) {
    return item.option_groups || [];
  }

  function itemNeedsConfig(item) {
    var prices = item.prices || [];
    return prices.length > 1 || itemOptionGroups(item).length > 0;
  }

  function itemHasPriceDeltas(item) {
    return itemOptionGroups(item).some(function (group) {
      return (group.choices || []).some(function (choice) {
        return Number(choice.price_delta || 0) !== 0;
      });
    });
  }

  function startingPrice(item) {
    var prices = item.prices || [];
    if (!prices.length) return 0;
    var minTier = Math.min.apply(
      null,
      prices.map(function (tier) {
        return Number(tier.price);
      })
    );
    var minDelta = itemOptionGroups(item).reduce(function (sum, group) {
      var deltas = (group.choices || []).map(function (choice) {
        return Number(choice.price_delta || 0);
      });
      return sum + (deltas.length ? Math.min.apply(null, deltas) : 0);
    }, 0);
    return minTier + minDelta;
  }

  function cardPriceText(item) {
    var prices = item.prices || [];
    if (!prices.length) return "";
    var amount = formatPrice(startingPrice(item)) + " " + currency();
    if (prices.length > 1 || itemHasPriceDeltas(item)) {
      return t("fromPrice") + " " + amount;
    }
    return amount;
  }

  function optionsDelta(options) {
    return (options || []).reduce(function (sum, choice) {
      return sum + Number(choice.price_delta || 0);
    }, 0);
  }

  function unitPriceFor(tier, options) {
    return Number((Number(tier.price) + optionsDelta(options)).toFixed(3));
  }

  function buildLineKey(itemId, tier, options) {
    var optionPart = (options || [])
      .map(function (choice) {
        return choice.label_en + ":" + Number(choice.price_delta || 0).toFixed(3);
      })
      .join(",");
    return itemId + "|" + tier.label_en + "|" + tier.price + "|" + optionPart;
  }

  function defaultOptionsFor(item) {
    return itemOptionGroups(item).map(function (group) {
      return (group.choices && group.choices[0]) || null;
    });
  }

  function syncCartPanelVisibility() {
    var open = cartPanelOpen;
    els.cartOverlay.classList.toggle("open", open);
    els.cartPanel.classList.toggle("open", open);
    els.cartPanel.setAttribute("aria-hidden", open ? "false" : "true");
    els.cartOverlay.setAttribute("aria-hidden", open ? "false" : "true");
  }

  function syncAddModalVisibility() {
    var open = addModalOpen;
    els.addOverlay.classList.toggle("open", open);
    els.addModal.classList.toggle("open", open);
    els.addModal.setAttribute("aria-hidden", open ? "false" : "true");
    els.addOverlay.setAttribute("aria-hidden", open ? "false" : "true");
    document.body.classList.toggle("modal-open", open);
  }

  function applyLanguage() {
    els.root.lang = lang;
    els.root.dir = lang === "ar" ? "rtl" : "ltr";
    els.langToggle.textContent = t("langBtn");
    els.cartTitle.textContent = t("cart");
    els.totalLabel.textContent = t("total");
    els.checkoutBtn.textContent = t("checkout");
    els.addTotalLabel.textContent = t("total");
    els.addConfirmBtn.textContent = t("addToCart");
    els.closeAdd.setAttribute("aria-label", t("close"));
    renderMenu();
    updateCartContents();
    syncCartPanelVisibility();
    if (addModalOpen && modalItem) {
      renderAddModal();
    }
    syncAddModalVisibility();
    setupScrollSpy();
  }

  function renderMenu() {
    if (!MENU_DATA.categories || !MENU_DATA.categories.length) {
      els.menuRoot.innerHTML = '<div class="empty-state">' + t("emptyMenu") + "</div>";
      els.categoryNav.innerHTML = "";
      return;
    }

    els.categoryNav.innerHTML = MENU_DATA.categories
      .map(function (cat) {
        return (
          '<a class="category-link" href="#cat-' +
          cat.id +
          '" data-category-id="' +
          cat.id +
          '">' +
          localizedName(cat) +
          "</a>"
        );
      })
      .join("");

    els.menuRoot.innerHTML = MENU_DATA.categories
      .map(function (cat) {
        var note = localizedNote(cat);
        return (
          '<section class="menu-section" id="cat-' +
          cat.id +
          '" data-category-id="' +
          cat.id +
          '">' +
          '<div class="menu-section-inner">' +
          '<h2 class="section-title">' +
          localizedName(cat) +
          "</h2>" +
          (note ? '<p class="section-note">' + note + "</p>" : "") +
          '<div class="items-grid">' +
          cat.items
            .map(function (item) {
              return renderItemCard(item);
            })
            .join("") +
          "</div></div></section>"
        );
      })
      .join("");

    bindMenuEvents();
  }

  function renderItemCard(item) {
    var imageHtml = item.image_url
      ? '<img src="' + item.image_url + '" alt="' + localizedName(item) + '" loading="lazy">'
      : '<div class="item-image-placeholder">' + t("noImage") + "</div>";

    return (
      '<article class="item-card" data-item-id="' +
      item.id +
      '">' +
      '<div class="item-image-wrap">' +
      imageHtml +
      "</div>" +
      '<div class="item-body">' +
      '<h3 class="item-name">' +
      localizedName(item) +
      "</h3>" +
      '<p class="item-price-single">' +
      cardPriceText(item) +
      "</p>" +
      '<div class="card-footer">' +
      '<button type="button" class="add-btn" data-item-id="' +
      item.id +
      '">' +
      t("add") +
      "</button>" +
      "</div></div></article>"
    );
  }

  function bindMenuEvents() {
    document.querySelectorAll(".add-btn").forEach(function (btn) {
      btn.addEventListener("click", function () {
        onAddClick(Number(btn.dataset.itemId));
      });
    });

    document.querySelectorAll(".category-link").forEach(function (link) {
      link.addEventListener("click", function (e) {
        e.preventDefault();
        var target = document.querySelector(link.getAttribute("href"));
        if (target) target.scrollIntoView({ behavior: "smooth", block: "start" });
      });
    });
  }

  function findItem(itemId) {
    for (var i = 0; i < MENU_DATA.categories.length; i++) {
      var cat = MENU_DATA.categories[i];
      for (var j = 0; j < cat.items.length; j++) {
        if (cat.items[j].id === itemId) return cat.items[j];
      }
    }
    return null;
  }

  function onAddClick(itemId) {
    var item = findItem(itemId);
    if (!item || !(item.prices || []).length) return;
    if (!itemNeedsConfig(item)) {
      addConfiguredLine(item, item.prices[0], [], 1);
      return;
    }
    openAddModal(item);
  }

  function openAddModal(item) {
    modalItem = item;
    modalTier = item.prices[0];
    modalOptions = defaultOptionsFor(item);
    modalQty = 1;
    addModalOpen = true;
    renderAddModal();
    els.addModal.classList.add("animating");
    els.addOverlay.classList.add("animating");
    syncAddModalVisibility();
    window.setTimeout(function () {
      if (addModalOpen) {
        els.addModal.classList.remove("animating");
        els.addOverlay.classList.remove("animating");
      }
    }, modalAnimMs);
  }

  function closeAddModal() {
    if (!addModalOpen) return;
    addModalOpen = false;
    els.addModal.classList.add("animating");
    els.addOverlay.classList.add("animating");
    syncAddModalVisibility();
    window.setTimeout(function () {
      els.addModal.classList.remove("animating");
      els.addOverlay.classList.remove("animating");
      if (!addModalOpen) {
        modalItem = null;
        modalTier = null;
        modalOptions = [];
        modalQty = 1;
        els.addModalBody.innerHTML = "";
      }
    }, modalAnimMs);
  }

  function renderAddModal() {
    if (!modalItem || !modalTier) return;

    els.addModalTitle.textContent = localizedName(modalItem);
    els.addQtyValue.textContent = String(modalQty);
    els.addConfirmBtn.textContent = t("addToCart");
    els.addTotalLabel.textContent = t("total");
    updateModalTotal();

    var imageHtml = modalItem.image_url
      ? '<img src="' +
        modalItem.image_url +
        '" alt="' +
        localizedName(modalItem) +
        '" class="add-modal-thumb">'
      : '<div class="add-modal-thumb placeholder">' + t("noImage") + "</div>";

    var prices = modalItem.prices || [];
    var tierHtml = "";
    if (prices.length > 1) {
      tierHtml =
        '<div class="option-group">' +
        '<p class="option-group-label">' +
        (lang === "ar" ? "الحجم / السعر" : "Size / Price") +
        "</p>" +
        '<div class="option-list modal-tier-list">' +
        prices
          .map(function (tier) {
            var active =
              modalTier.label_en === tier.label_en &&
              Number(modalTier.price) === Number(tier.price)
                ? " active"
                : "";
            return (
              '<button type="button" class="option-pill' +
              active +
              '" data-modal-tier-key="' +
              tierKey(modalItem.id, tier) +
              '">' +
              localizedTier(tier) +
              " " +
              formatPrice(tier.price) +
              "</button>"
            );
          })
          .join("") +
        "</div></div>";
    }

    var optionsHtml = itemOptionGroups(modalItem)
      .map(function (group, groupIndex) {
        var activeChoice = modalOptions[groupIndex] || group.choices[0];
        return (
          '<div class="option-group" data-group-index="' +
          groupIndex +
          '">' +
          '<p class="option-group-label">' +
          localizedGroup(group) +
          "</p>" +
          '<div class="option-list">' +
          (group.choices || [])
            .map(function (choice) {
              var active =
                activeChoice &&
                activeChoice.label_en === choice.label_en &&
                Number(activeChoice.price_delta || 0) === Number(choice.price_delta || 0)
                  ? " active"
                  : "";
              var delta = Number(choice.price_delta || 0);
              var deltaHtml =
                delta > 0
                  ? ' <span class="option-delta">+' + formatPrice(delta) + "</span>"
                  : "";
              return (
                '<button type="button" class="option-pill' +
                active +
                '" data-group-index="' +
                groupIndex +
                '" data-choice-key="' +
                choiceKey(choice) +
                '">' +
                localizedChoice(choice) +
                deltaHtml +
                "</button>"
              );
            })
            .join("") +
          "</div></div>"
        );
      })
      .join("");

    els.addModalBody.innerHTML =
      '<div class="add-modal-hero">' +
      imageHtml +
      '<div class="add-modal-hero-text">' +
      '<p class="add-modal-name">' +
      localizedName(modalItem) +
      "</p>" +
      '<p class="add-modal-base-price">' +
      formatPrice(Number(modalTier.price)) +
      " " +
      currency() +
      "</p>" +
      "</div></div>" +
      tierHtml +
      optionsHtml;

    bindModalEvents();
  }

  function bindModalEvents() {
    els.addModalBody.querySelectorAll("[data-modal-tier-key]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var tier = modalItem.prices.find(function (p) {
          return tierKey(modalItem.id, p) === btn.dataset.modalTierKey;
        });
        if (!tier) return;
        modalTier = tier;
        renderAddModal();
      });
    });

    els.addModalBody.querySelectorAll("[data-choice-key]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var groupIndex = Number(btn.dataset.groupIndex);
        var group = itemOptionGroups(modalItem)[groupIndex];
        if (!group) return;
        var choice = (group.choices || []).find(function (c) {
          return choiceKey(c) === btn.dataset.choiceKey;
        });
        if (!choice) return;
        modalOptions[groupIndex] = choice;
        renderAddModal();
      });
    });
  }

  function updateModalTotal() {
    if (!modalItem || !modalTier) return;
    var unit = unitPriceFor(modalTier, modalOptions.filter(Boolean));
    var total = unit * modalQty;
    els.addModalTotal.textContent = formatPrice(total) + " " + currency();
  }

  function confirmAddFromModal() {
    if (!modalItem || !modalTier) return;
    addConfiguredLine(
      modalItem,
      modalTier,
      modalOptions.filter(Boolean),
      modalQty
    );
    closeAddModal();
  }

  function addConfiguredLine(item, tier, options, quantity) {
    var qty = Math.max(1, Number(quantity) || 1);
    var lineKey = buildLineKey(item.id, tier, options);
    var existing = cart.find(function (line) {
      return line.line_key === lineKey;
    });
    if (existing) {
      existing.quantity += qty;
    } else {
      cart.push({
        line_key: lineKey,
        item_id: item.id,
        name_ar: item.name_ar,
        name_en: item.name_en,
        tier_label_ar: tier.label_ar,
        tier_label_en: tier.label_en,
        options: options.map(function (choice) {
          return {
            label_ar: choice.label_ar,
            label_en: choice.label_en,
            price_delta: Number(choice.price_delta || 0),
          };
        }),
        unit_price: unitPriceFor(tier, options),
        quantity: qty,
      });
    }
    saveCart();
    updateCartContents();
  }

  function cartCount() {
    return cart.reduce(function (sum, line) {
      return sum + line.quantity;
    }, 0);
  }

  function cartTotal() {
    return cart.reduce(function (sum, line) {
      return sum + line.quantity * line.unit_price;
    }, 0);
  }

  function lineOptionsText(line) {
    var options = line.options || [];
    if (!options.length) {
      var onlyTier = lang === "ar" ? line.tier_label_ar : line.tier_label_en;
      if (onlyTier === "Price" || onlyTier === "السعر") return "";
      return onlyTier;
    }
    var labels = options.map(function (choice) {
      return lang === "ar" ? choice.label_ar : choice.label_en;
    });
    var tierLabel = lang === "ar" ? line.tier_label_ar : line.tier_label_en;
    if (tierLabel && tierLabel !== "Price" && tierLabel !== "السعر") {
      return tierLabel + " · " + labels.join(" · ");
    }
    return labels.join(" · ");
  }

  function updateCartContents() {
    var count = cartCount();
    els.cartBadge.textContent = count;
    els.cartFab.classList.toggle("visible", count > 0);
    els.checkoutBtn.disabled = count === 0;
    els.cartTotal.textContent = formatPrice(cartTotal()) + " " + currency();

    if (!count) {
      els.cartLines.innerHTML = '<div class="cart-empty">' + t("emptyCart") + "</div>";
      return;
    }

    els.cartLines.innerHTML = cart
      .map(function (line) {
        var name = lang === "ar" ? line.name_ar : line.name_en;
        var detail = lineOptionsText(line);
        var subtotal = line.quantity * line.unit_price;
        return (
          '<div class="cart-line" data-line-key="' +
          line.line_key +
          '">' +
          '<div><p class="line-name">' +
          name +
          "</p>" +
          (detail ? '<p class="line-tier">' + detail + "</p>" : "") +
          '<p class="line-subtotal">' +
          formatPrice(subtotal) +
          " " +
          currency() +
          "</p></div>" +
          '<div class="line-controls">' +
          '<div class="qty-controls">' +
          '<button type="button" class="qty-btn" data-action="dec" data-line-key="' +
          line.line_key +
          '">−</button>' +
          "<span>" +
          line.quantity +
          "</span>" +
          '<button type="button" class="qty-btn" data-action="inc" data-line-key="' +
          line.line_key +
          '">+</button>' +
          "</div>" +
          '<button type="button" class="remove-line" data-action="remove" data-line-key="' +
          line.line_key +
          '">' +
          t("remove") +
          "</button></div></div>"
        );
      })
      .join("");

    els.cartLines.querySelectorAll("[data-action]").forEach(function (btn) {
      btn.addEventListener("click", function () {
        updateLine(btn.dataset.lineKey, btn.dataset.action);
      });
    });
  }

  function updateLine(lineKey, action) {
    var idx = cart.findIndex(function (line) {
      return line.line_key === lineKey;
    });
    if (idx === -1) return;
    if (action === "inc") cart[idx].quantity += 1;
    if (action === "dec") cart[idx].quantity -= 1;
    if (action === "remove" || cart[idx].quantity <= 0) cart.splice(idx, 1);
    saveCart();
    updateCartContents();
  }

  function setCartPanelAnimating(active) {
    els.cartPanel.classList.toggle("animating", active);
    els.cartOverlay.classList.toggle("animating", active);
  }

  function openCart() {
    if (addModalOpen) closeAddModal();
    cartPanelOpen = true;
    setCartPanelAnimating(true);
    syncCartPanelVisibility();
    window.setTimeout(function () {
      if (cartPanelOpen) setCartPanelAnimating(false);
    }, cartAnimMs);
  }

  function closeCartPanel() {
    if (!cartPanelOpen) return;
    cartPanelOpen = false;
    setCartPanelAnimating(true);
    syncCartPanelVisibility();
    window.setTimeout(function () {
      setCartPanelAnimating(false);
    }, cartAnimMs);
  }

  function buildWhatsAppMessage() {
    var lines = [t("orderTitle"), ""];
    cart.forEach(function (line) {
      var name = lang === "ar" ? line.name_ar : line.name_en;
      var detail = lineOptionsText(line);
      var subtotal = line.quantity * line.unit_price;
      lines.push(
        line.quantity +
          "x " +
          name +
          (detail ? " (" + detail + ")" : "") +
          " - " +
          formatPrice(subtotal) +
          " " +
          currency()
      );
    });
    lines.push("");
    lines.push(t("total") + ": " + formatPrice(cartTotal()) + " " + currency());
    return lines.join("\n");
  }

  function checkoutWhatsApp() {
    if (!cart.length) return;
    var message = buildWhatsAppMessage();
    var url =
      "https://wa.me/" +
      MENU_DATA.whatsapp_number +
      "?text=" +
      encodeURIComponent(message);
    window.open(url, "_blank");
  }

  function setupScrollSpy() {
    var sections = document.querySelectorAll(".menu-section");
    var links = document.querySelectorAll(".category-link");
    if (!sections.length || !links.length) return;

    if (window._hikayaScrollSpy) {
      window.removeEventListener("scroll", window._hikayaScrollSpy);
    }

    window._hikayaScrollSpy = function () {
      var offset = 130;
      var currentId = sections[0].dataset.categoryId;
      sections.forEach(function (section) {
        if (window.scrollY + offset >= section.offsetTop) {
          currentId = section.dataset.categoryId;
        }
      });
      links.forEach(function (link) {
        link.classList.toggle("active", link.dataset.categoryId === currentId);
      });
    };

    window.addEventListener("scroll", window._hikayaScrollSpy, { passive: true });
    window._hikayaScrollSpy();
  }

  els.langToggle.addEventListener("click", function () {
    lang = lang === "ar" ? "en" : "ar";
    localStorage.setItem("hikaya_lang", lang);
    applyLanguage();
  });

  els.cartFab.addEventListener("click", openCart);
  els.closeCart.addEventListener("click", closeCartPanel);
  els.cartOverlay.addEventListener("click", closeCartPanel);
  els.checkoutBtn.addEventListener("click", checkoutWhatsApp);

  els.closeAdd.addEventListener("click", closeAddModal);
  els.addOverlay.addEventListener("click", closeAddModal);
  els.addConfirmBtn.addEventListener("click", confirmAddFromModal);
  els.addQtyDec.addEventListener("click", function () {
    if (modalQty > 1) {
      modalQty -= 1;
      els.addQtyValue.textContent = String(modalQty);
      updateModalTotal();
    }
  });
  els.addQtyInc.addEventListener("click", function () {
    modalQty += 1;
    els.addQtyValue.textContent = String(modalQty);
    updateModalTotal();
  });

  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape" && addModalOpen) {
      closeAddModal();
    }
  });

  readMenuData();
  loadCart();
  cartPanelOpen = false;
  addModalOpen = false;
  setCartPanelAnimating(false);
  syncCartPanelVisibility();
  syncAddModalVisibility();
  applyLanguage();
})();
