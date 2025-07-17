/**
 * مولد الباركود البسيط
 * يحول النص إلى باركود باستخدام CSS و JavaScript فقط
 */

class BarcodeGenerator {
    constructor() {
        // نمط الخطوط للباركود Code 128 مبسط
        this.patterns = {
            '0': '11011001100',
            '1': '11001101100',
            '2': '11001100110',
            '3': '10010011000',
            '4': '10010001100',
            '5': '10001001100',
            '6': '10011001000',
            '7': '10011000100',
            '8': '10001100100',
            '9': '11001001000',
            'A': '11001000100',
            'B': '11000100100',
            'C': '10110011100',
            'D': '10011011100',
            'E': '10011001110',
            'F': '10111001000',
            'G': '10011101000',
            'H': '10011100100',
            'I': '11001110010',
            'J': '11001011100',
            'K': '11001001110',
            'L': '11011100100',
            'M': '11001110100',
            'N': '11101101110',
            'O': '11101001100',
            'P': '11100101100',
            'Q': '11100100110',
            'R': '11101100100',
            'S': '11100110100',
            'T': '11100110010',
            'U': '11011011000',
            'V': '11011000110',
            'W': '11000110110',
            'X': '10100011000',
            'Y': '10001011000',
            'Z': '10001000110',
            ' ': '10110001000',
            'START': '11010000100',
            'STOP': '1100011101011'
        };
    }

    /**
     * إنشاء باركود من النص
     * @param {string} text - النص المراد تحويله
     * @param {string} containerId - معرف العنصر الذي سيحتوي على الباركود
     * @param {object} options - خيارات التخصيص
     */
    generateBarcode(text, containerId, options = {}) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error('Container not found:', containerId);
            return;
        }

        // الخيارات الافتراضية
        const settings = {
            width: options.width || 2,
            height: options.height || 50,
            fontSize: options.fontSize || 12,
            showText: options.showText !== false,
            backgroundColor: options.backgroundColor || '#ffffff',
            foregroundColor: options.foregroundColor || '#000000',
            ...options
        };

        // تنظيف النص
        const cleanText = text.toString().toUpperCase().replace(/[^A-Z0-9 ]/g, '');
        
        // إنشاء نمط الباركود
        let barcodePattern = this.patterns['START'];
        
        for (let char of cleanText) {
            if (this.patterns[char]) {
                barcodePattern += this.patterns[char];
            } else {
                // استخدام نمط افتراضي للأحرف غير المدعومة
                barcodePattern += this.patterns['0'];
            }
        }
        
        barcodePattern += this.patterns['STOP'];

        // إنشاء HTML للباركود
        container.innerHTML = this.createBarcodeHTML(barcodePattern, cleanText, settings);
    }

    /**
     * إنشاء HTML للباركود
     */
    createBarcodeHTML(pattern, text, settings) {
        let barsHTML = '';
        
        for (let i = 0; i < pattern.length; i++) {
            const isBar = pattern[i] === '1';
            const width = settings.width;
            const color = isBar ? settings.foregroundColor : settings.backgroundColor;
            
            barsHTML += `<div class="barcode-bar" style="
                width: ${width}px;
                height: ${settings.height}px;
                background-color: ${color};
                display: inline-block;
                margin: 0;
                padding: 0;
            "></div>`;
        }

        const textDisplay = settings.showText ? `
            <div class="barcode-text" style="
                text-align: center;
                font-family: monospace;
                font-size: ${settings.fontSize}px;
                margin-top: 5px;
                color: ${settings.foregroundColor};
            ">${text}</div>
        ` : '';

        return `
            <div class="barcode-container" style="
                display: inline-block;
                background-color: ${settings.backgroundColor};
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
            ">
                <div class="barcode-bars" style="
                    line-height: 0;
                    font-size: 0;
                ">
                    ${barsHTML}
                </div>
                ${textDisplay}
            </div>
        `;
    }

    /**
     * إنشاء باركود مبسط باستخدام خطوط
     */
    generateSimpleBarcode(text, containerId, options = {}) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error('Container not found:', containerId);
            return;
        }

        const settings = {
            width: options.width || 200,
            height: options.height || 50,
            fontSize: options.fontSize || 12,
            showText: options.showText !== false,
            ...options
        };

        // إنشاء باركود مبسط باستخدام خطوط عمودية
        const cleanText = text.toString();
        const barsCount = cleanText.length * 6; // 6 خطوط لكل حرف
        
        let barsHTML = '';
        for (let i = 0; i < barsCount; i++) {
            const isThick = (i + cleanText.charCodeAt(i % cleanText.length)) % 3 === 0;
            const barWidth = isThick ? 3 : 1;
            const spacing = i < barsCount - 1 ? 1 : 0;
            
            barsHTML += `<div style="
                width: ${barWidth}px;
                height: ${settings.height}px;
                background-color: #000;
                display: inline-block;
                margin-right: ${spacing}px;
            "></div>`;
        }

        const textDisplay = settings.showText ? `
            <div style="
                text-align: center;
                font-family: monospace;
                font-size: ${settings.fontSize}px;
                margin-top: 5px;
                letter-spacing: 2px;
            ">${cleanText}</div>
        ` : '';

        container.innerHTML = `
            <div style="
                display: inline-block;
                background-color: white;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                text-align: center;
            ">
                <div style="
                    line-height: 0;
                    font-size: 0;
                    width: ${settings.width}px;
                    overflow: hidden;
                ">
                    ${barsHTML}
                </div>
                ${textDisplay}
            </div>
        `;
    }

    /**
     * طباعة الباركود
     */
    printBarcode(containerId) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error('Container not found:', containerId);
            return;
        }

        const printWindow = window.open('', '_blank');
        printWindow.document.write(`
            <html>
                <head>
                    <title>طباعة الباركود</title>
                    <style>
                        body { 
                            margin: 0; 
                            padding: 20px; 
                            font-family: Arial, sans-serif;
                            text-align: center;
                        }
                        @media print {
                            body { margin: 0; padding: 10px; }
                        }
                    </style>
                </head>
                <body>
                    ${container.innerHTML}
                    <script>
                        window.onload = function() {
                            window.print();
                            window.close();
                        }
                    </script>
                </body>
            </html>
        `);
        printWindow.document.close();
    }
}

// إنشاء مثيل عام
window.BarcodeGenerator = new BarcodeGenerator();

// دوال مساعدة للاستخدام السهل
window.generateBarcode = function(text, containerId, options) {
    window.BarcodeGenerator.generateBarcode(text, containerId, options);
};

window.generateSimpleBarcode = function(text, containerId, options) {
    window.BarcodeGenerator.generateSimpleBarcode(text, containerId, options);
};

window.printBarcode = function(containerId) {
    window.BarcodeGenerator.printBarcode(containerId);
};
