using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Xml.Linq;
using Excel = Microsoft.Office.Interop.Excel;
using Office = Microsoft.Office.Core;
using Microsoft.Office.Tools.Excel;
using System.Threading;
using ZeroMQ;
using System.Threading;

namespace comnsense
{
    public partial class ThisAddIn
    {
        private ZContext context;
        private EventPublisher publisher;
        private Thread router;
        private CancellationTokenSource canceller;

        private void ThisAddIn_Startup(object sender, System.EventArgs e)
        {
            this.context = new ZContext();
            this.router = new Thread(() =>
            {
                Router r = new Router(this.context, this.Application);
                r.Run(this.canceller.Token);
            });
            this.Application.WorkbookOpen += new Excel.AppEvents_WorkbookOpenEventHandler(ThisAddIn_WorkbookOpen);
            this.Application.WorkbookBeforeClose += new Excel.AppEvents_WorkbookBeforeCloseEventHandler(ThisAddIn_WorkbookBeforeClose);
            this.Application.SheetChange += new Excel.AppEvents_SheetChangeEventHandler(ThisAddIn_SheetChange);
            this.Application.WorkbookBeforeClose += new Excel.AppEvents_WorkbookBeforeCloseEventHandler(ThisAddIn_BeforeClose);
        }

        private void ThisAddIn_Shutdown(object sender, System.EventArgs e)
        {
            this.router.Join();
        }

        void ThisAddIn_WorkbookOpen(Excel.Workbook wb)
        {
            Ident ident = new Ident(wb);
            if (ident.get() == null)
            {
                // get ident from agent
                ident.set(System.Guid.NewGuid().ToString());
            }
            this.publisher.Send(Event.WorkbookOpen(wb));
        }

        private void ThisAddIn_WorkbookBeforeClose(Excel.Workbook wb, ref bool result)
        {
            this.publisher.Send(Event.WorkbookBeforeClose(wb));
        }

        private void ThisAddIn_BeforeClose(Excel.Workbook wb, ref bool result)
        {
            this.canceller.Cancel();
        }

        private void ThisAddIn_SheetChange(object sh, Excel.Range target)
        {
            this.publisher.Send(Event.SheetChange((sh as Excel.Worksheet), target));
        }

        #region Код, автоматически созданный VSTO

        /// <summary>
        /// Обязательный метод для поддержки конструктора - не изменяйте
        /// содержимое данного метода при помощи редактора кода.
        /// </summary>
        private void InternalStartup()
        {
            this.Startup += new System.EventHandler(ThisAddIn_Startup);
            this.Shutdown += new System.EventHandler(ThisAddIn_Shutdown);
        }
        
        #endregion
    }
}
