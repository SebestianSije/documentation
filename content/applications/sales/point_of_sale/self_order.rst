=============
Self-ordering
=============

The self-ordering feature allows customers to browse your menu or product catalog, place an order,
and complete payment using their mobile device or a self-ordering kiosk.

Configuration
=============

To enable this feature, access the :ref:`POS settings <configuration/settings>`, scroll down to the
:guilabel:`Mobile self-order & Kiosk` section, and select a :guilabel:`Self Ordering` type under the
:guilabel:`QR menu & Kiosk activation` section. You can choose from:

.. tabs::

   .. group-tab:: QR menu

      Select :guilabel:`QR menu` or :guilabel:`Qr menu + Ordering` to give customers access to your
      menu on their personal device by scanning a QR code. The latter also allows them to place an
      order and make a payment.

      .. image:: self_order/qr-activation.png
         :alt: QR menu and kiosk setting activation

      - Click :icon:`fa-arrow-right` :guilabel:`Print QR Codes` to download a .pdf document with the
        generated QR codes.
      - Click :icon:`fa-arrow-right` :guilabel:`Download QR Codes` to download a compressed file with
        the generated QR codes.

      .. note::
         - In **restaurants**, printing or downloading QR codes generates as many QR codes as the
           number of available tables.
         - In **shops**, it generates only one generic QR code.
         - Once a self-ordering type is selected, the setup form alters to fit the selected type's
           needs.

      .. tip::
         To customize QR codes,

         #. Scan the relevant QR code to acquire its URL.
         #. Using a QR code generator like `QR code monkey <https://www.qrcode-monkey.com>`_ or `QR
            code generator <https://www.qr-code-generator.com>`_, generate a customized QR code that
            redirects to this URL.

   .. group-tab:: Kiosk

      When :guilabel:`Kiosk` is set, customers can access the menu, place orders and pay from a
      self-ordering kiosk.

      .. image:: self_order/kiosk-activation.png
         :alt: QR menu and kiosk setting activation

      .. note::
         Once a self-ordering type is selected, the setup form alters to fit the selected type's
         needs.

Sub-settings
------------

.. tabs::

   .. tab:: Home buttons

      To set up the buttons available on-screen, click :icon:`fa-arrow-right` :guilabel:`Home
      buttons`. Then,

      #. Click :guilabel:`New` to add a new button.
      #. Set the :guilabel:`Label`.
      #. Enter a :guilabel:`URL` preceded by :guilabel:`https://` to redirect customers to a
         specific URL when clicking the button.

         - To redirect them to the product menu, enter `/products` in that column.
      #. Select the :guilabel:`Points of Sale` to ensure this button only appear on the selected
         POS' self-ordering interface.
      #. Select a predefined :guilabel:`Style` from the dropdown menu.

      .. note::
         - Leaving the :guilabel:`Points of Sale` field empty automatically shares the button with
           all POS.
         - The button is automatically updated in the :guilabel:`Preview` column.

   .. tab:: Service location and payment options

      - Set where the service takes place by selecting :guilabel:`Table` or :guilabel:`Pickup zone`
        under the :guilabel:`Service` field.
      - Set when and how customers can pay in the :guilabel:`Pay after` field. Customers can either
        pay after :guilabel:`Each meal` or :guilabel:`Each order`.
      - Depending on the type of self-ordering service and POS, the service location and
        payment options slightly differs:

        - **QR menu**:

          - **Restaurants**: customers can be served at their table or at the pickup zone.

            - When served at their table, they can either pay after each meal or each order.
            - When served at the pickup zone, they can only pay after each order.
          - **Shops**: customers can only be served at pickup zone and pay after each order
          - Regardless of the type of POS, customers can pay using any configured payment
            method or online.

        - **Kiosk**:

          - Regardless of the type of POS, customers can either be served at their table or the
            pickup zone, but they have to pay after each order.
          - The kiosk self-ordering only works with Adyen & Stripe terminals.
          - :guilabel:`Online Payment` are not supported.

      .. seealso::
         - :doc:`../../finance/payment_providers`
         - :doc:`payment_methods`

   .. tab:: Language

      This option allows you to enable multiple language options for the self-ordering interface.
      The suggested languages are the languages already installed in Odoo. To add more languages to
      choose from,

      #. Click :icon:`fa-arrow-right` :guilabel:`Add Languages`.
      #. Add as many languages as needed to the :guilabel:`Languages` field.
      #. Click :guilabel:`Add`.
      #. Add those languages to the :guilabel:`Available` field.

   .. tab:: Splash screens

      Splash screens are introductory screens displayed when the self-ordering interface or kiosk is
      launched. They typically contain branding, welcome messages, or usage instructions. To add a
      splash screen image, click :icon:`fa-paperclip` :guilabel:`Add images`, select and open an
      image. To remove a splash screen image, hover over an image and click :icon:`fa-times`.

      .. note::
         You can add multiple splash screen images at once.

   .. tab:: Eat in/ Take out

      Set it up to :doc:`use multiple fiscal positions <pricing/fiscal_position>` depending on
      whether customers eat in or take their order to go.

      .. seealso::
         :doc:`pricing/fiscal_position`

   .. tab:: Preview

      Click :icon:`fa-arrow-right` :guilabel:`Preview Web interface` under the :guilabel:`Self
      Ordering` field to ensure the interface fits your needs.

Practical application
=====================

.. tabs::

   .. group-tab:: QR menu

      On the POS user's end,

      #. Open a POS session for the feature to be available to customers.
      #. To access the self-ordering interface, scan a downloaded or printed QR code, or click the
         vertical ellipsis (:icon:`fa-ellipsis-v`) on the POS card and :guilabel:`Mobile Menu`.

      On the customers' end,

      #. To access the self-ordering interface, scan a downloaded or printed QR code.
      #. Click the configured home button to reach the menu or catalog.
      #. Select the items and click :guilabel:`Order` to place an order.
      #. Follow the instructions on-screen to assign a table and pay for the order.

      Once an order is placed, it is automatically sent to the preparation screen, and added to the
      list of POS orders.

      .. important::
         A POS session must be open for customers to place an order.

   .. group-tab:: Kiosk

      On the POS user's end,

      #. Click :guilabel:`Start Kiosk`.
      #. Open the provided URL on the self-ordering kiosk(s).

         - Copy and paste it, or
         - Click :guilabel:`Open in New Tab`.

      .. note::
         Click :guilabel:`Open Kiosk` on the POS card to reopen the popup window and access the
         self-ordering interface.

      On the customers' end,

      #. From a configured self-ordering kiosk, click the home button to reach the menu or catalog.
      #. Select the items and click :guilabel:`Order` to place an order.
      #. Follow the instructions on-screen to assign a table and pay for the order.

      .. image:: self_order/kiosk-endscreen.png
         :alt: kiosk end-screen for customers
         :scale: 65 %

      Once an order is placed, it is automatically sent to the preparation screen, and added to the
      list of POS orders.

      .. important::
         A POS session must be open for customers to place an order.
