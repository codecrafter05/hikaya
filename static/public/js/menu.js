(function () {
  "use strict";

  var MENU_DATA = {};
  var cart = [];
  var lang = localStorage.getItem("hikaya_lang") || "ar";
  var selectedTiers = {};
  var cartPanelOpen = false;
  var cartAnimMs = 280;

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

  function formatPrice(value) {
    return Number(value).toFixed(3);
  }

  function localizedName(obj) {
    return lang === "ar" ? obj.name_ar : obj.name_en;
  }

  function localizedDesc(obj) {
    return lang === "ar" ? obj.description_ar : obj.description_en;
  }

  function localizedTier(tier) {
    return lang === "ar" ? tier.label_ar : tier.label_en;
  }

  function syncCartPanelVisibility() {
    var open = cartPanelOpen;
    els.cartOverlay.classList.toggle("open", open);
    els.cartPanel.classList.toggle("open", open);
    els.cartPanel.setAttribute("aria-hidden", open ? "false" : "true");
    els.cartOverlay.setAttribute("aria-hidden", open ? "false" : "true");
  }

  function applyLanguage() {
    els.root.lang = lang;
    els.root.dir = lang === "ar" ? "rtl" : "ltr";
    els.langToggle.textContent = t("langBtn");
    els.cartTitle.textContent = t("cart");
    els.totalLabel.textContent = t("total");
    els.checkoutBtn.textContent = t("checkout");
    renderMenu();
    updateCartContents();
    syncCartPanelVisibility();
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
    var prices = item.prices || [];
    var selected = selectedTiers[item.id] || prices[0];
    var desc = localizedDesc(item);
    var imageHtml = item.image_url
      ? '<img src="' + item.image_url + '" alt="' + localizedName(item) + '">'
      : '<div class="item-image-placeholder">' + t("noImage") + "</div>";

    var priceHtml = "";
    if (prices.length > 1) {
      priceHtml =
        '<div class="tier-list" data-item-id="' +
        item.id +
        '">' +
        prices
          .map(function (tier) {
            var active =
              selected &&
              selected.label_en === tier.label_en &&
              selected.price === tier.price
                ? " active"
                : "";
            return (
              '<button type="button" class="tier-pill' +
              active +
              '" data-item-id="' +
              item.id +
              '" data-tier-key="' +
              tierKey(item.id, tier) +
              '">' +
              localizedTier(tier) +
              " " +
              formatPrice(tier.price) +
              "</button>"
            );
          })
          .join("") +
        "</div>";
    } else if (prices.length === 1) {
      priceHtml =
        '<p class="item-price-single">' +
        formatPrice(prices[0].price) +
        " " +
        MENU_DATA.currency_label +
        "</p>";
    }

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
      (desc ? '<p class="item-desc">' + desc + "</p>" : "") +
      priceHtml +
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
    document.querySelectorAll(".tier-pill").forEach(function (btn) {
      btn.addEventListener("click", function () {
        var itemId = Number(btn.dataset.itemId);
        var item = findItem(itemId);
        if (!item) return;
        var tier = item.prices.find(function (p) {
          return tierKey(itemId, p) === btn.dataset.tierKey;
        });
        selectedTiers[itemId] = tier;
        btn.closest(".tier-list").querySelectorAll(".tier-pill").forEach(function (pill) {
          pill.classList.remove("active");
        });
        btn.classList.add("active");
      });
    });

    document.querySelectorAll(".add-btn").forEach(function (btn) {
      btn.addEventListener("click", function () {
        addToCart(Number(btn.dataset.itemId));
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

  function addToCart(itemId) {
    var item = findItem(itemId);
    if (!item || !item.prices.length) return;
    var tier = selectedTiers[itemId] || item.prices[0];
    var lineKey = itemId + "|" + tier.label_en + "|" + tier.price;
    var existing = cart.find(function (line) {
      return line.line_key === lineKey;
    });
    if (existing) {
      existing.quantity += 1;
    } else {
      cart.push({
        line_key: lineKey,
        item_id: itemId,
        name_ar: item.name_ar,
        name_en: item.name_en,
        tier_label_ar: tier.label_ar,
        tier_label_en: tier.label_en,
        unit_price: tier.price,
        quantity: 1,
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

  function updateCartContents() {
    var count = cartCount();
    els.cartBadge.textContent = count;
    els.cartFab.classList.toggle("visible", count > 0);
    els.checkoutBtn.disabled = count === 0;
    els.cartTotal.textContent = formatPrice(cartTotal()) + " " + MENU_DATA.currency_label;

    if (!count) {
      els.cartLines.innerHTML = '<div class="cart-empty">' + t("emptyCart") + "</div>";
      return;
    }

    els.cartLines.innerHTML = cart
      .map(function (line) {
        var name = lang === "ar" ? line.name_ar : line.name_en;
        var tier = lang === "ar" ? line.tier_label_ar : line.tier_label_en;
        var subtotal = line.quantity * line.unit_price;
        return (
          '<div class="cart-line" data-line-key="' +
          line.line_key +
          '">' +
          '<div><p class="line-name">' +
          name +
          "</p>" +
          '<p class="line-tier">' +
          tier +
          "</p>" +
          '<p class="line-subtotal">' +
          formatPrice(subtotal) +
          " " +
          MENU_DATA.currency_label +
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
      var tier = lang === "ar" ? line.tier_label_ar : line.tier_label_en;
      var subtotal = line.quantity * line.unit_price;
      lines.push(
        line.quantity +
          "x " +
          name +
          " (" +
          tier +
          ") - " +
          formatPrice(subtotal) +
          " " +
          MENU_DATA.currency_label
      );
    });
    lines.push("");
    lines.push(t("total") + ": " + formatPrice(cartTotal()) + " " + MENU_DATA.currency_label);
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

  function initSelectedTiers() {
    MENU_DATA.categories.forEach(function (cat) {
      cat.items.forEach(function (item) {
        if (item.prices && item.prices.length) {
          selectedTiers[item.id] = item.prices[0];
        }
      });
    });
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

  readMenuData();
  loadCart();
  initSelectedTiers();
  cartPanelOpen = false;
  setCartPanelAnimating(false);
  syncCartPanelVisibility();
  applyLanguage();
})();
