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

namespace comnsense
{
    public partial class ThisAddIn
    {
        private ZContext context;
        private EventPublisher publisher;
        private Dictionary<string, KeyValuePair<Thread, CancellationTokenSource>> routers;
        private Dictionary<string, Cell[][]> lastSelectedValues;

        private void ThisAddIn_Startup(object sender, System.EventArgs e)
        {
            this.context = new ZContext();
            this.publisher = new EventPublisher(this.context);
            this.routers = new Dictionary<string, KeyValuePair<Thread, CancellationTokenSource>>();
            this.lastSelectedValues = new Dictionary<string, Cell[][]>();
            this.Application.WorkbookOpen += new Excel.AppEvents_WorkbookOpenEventHandler(ThisAddIn_WorkbookOpen);
            this.Application.WorkbookBeforeClose += new Excel.AppEvents_WorkbookBeforeCloseEventHandler(ThisAddIn_WorkbookBeforeClose);
            this.Application.SheetSelectionChange += new Excel.AppEvents_SheetSelectionChangeEventHandler(ThisAddIn_SheetSelectionChange);
            this.Application.SheetChange += new Excel.AppEvents_SheetChangeEventHandler(ThisAddIn_SheetChange);
            this.Application.WorkbookBeforeClose += new Excel.AppEvents_WorkbookBeforeCloseEventHandler(ThisAddIn_BeforeClose);
            ((Excel.AppEvents_Event)this.Application).NewWorkbook += new Excel.AppEvents_NewWorkbookEventHandler(ThisAddIn_NewWorkbook);
        }

        private void ThisAddIn_Shutdown(object sender, System.EventArgs e)
        {
            foreach (KeyValuePair<String, KeyValuePair<Thread, CancellationTokenSource>> pair in this.routers)
            {
                Thread thread = pair.Value.Key;
                thread.Join();
            }
        }

        void ThisAddIn_WorkbookOpen(Excel.Workbook wb)
        {
            String ident = GetWorkbookIdent(wb);
            RunRouter(ident);
            this.publisher.Send(Event.WorkbookOpen(ident, wb));
        }

        void ThisAddIn_NewWorkbook(Excel.Workbook wb)
        {
            String ident = GetWorkbookIdent(wb);
            RunRouter(ident);
            this.publisher.Send(Event.WorkbookOpen(ident, wb));
        }

        private void ThisAddIn_WorkbookBeforeClose(Excel.Workbook wb, ref bool result)
        {
            String ident = GetWorkbookIdent(wb);
            this.publisher.Send(Event.WorkbookBeforeClose(ident, wb));
        }

        private void ThisAddIn_BeforeClose(Excel.Workbook wb, ref bool result)
        {
            String ident = GetWorkbookIdent(wb);
            if (this.routers.ContainsKey(ident)) {
                KeyValuePair<Thread, CancellationTokenSource> pair;
                if (this.routers.TryGetValue(ident, out pair)) {
                    pair.Value.Cancel();
                }
            }
        }

        private void ThisAddIn_SheetSelectionChange(object sh, Excel.Range target)
        {
            Excel.Workbook wb = ((Excel.Worksheet)sh).Parent;
            String ident = GetWorkbookIdent(wb);
            if (this.lastSelectedValues.ContainsKey(ident)) {
                this.lastSelectedValues[ident] = Event.GetCellsFromRange(target);
            }
            else
            {
                this.lastSelectedValues.Add(ident, Event.GetCellsFromRange(target));
            }
        }

        private void ThisAddIn_SheetChange(object sh, Excel.Range target)
        {
            Excel.Workbook wb = ((Excel.Worksheet)sh).Parent;
            String ident = GetWorkbookIdent(wb);
            if (this.lastSelectedValues.ContainsKey(ident))
            {
                this.publisher.Send(
                    Event.SheetChange(ident, (sh as Excel.Worksheet), target, this.lastSelectedValues[ident])
                );
            }
        }

        private String GetWorkbookIdent(Excel.Workbook wb)
        {
            Ident ident = new Ident(wb);
            if (ident.get() == null)
            {
                ident.set(System.Guid.NewGuid().ToString());
            }
            return ident.ToString();
        }

        private void RunRouter(String ident)
        {
            KeyValuePair<Thread, CancellationTokenSource> pair;
            if (this.routers.TryGetValue(ident, out pair))
            {
                if ((!pair.Key.IsAlive) || (pair.Value.IsCancellationRequested))
                {
                    this.routers.Remove(ident);
                }
            }
            if (!routers.ContainsKey(ident))
            {
                CancellationTokenSource canceller = new System.Threading.CancellationTokenSource();
                Thread router = new Thread(() =>
                {
                    Router r = new Router(this.context, this.Application, ident);
                    r.Run(canceller.Token);
                });
                routers.Add(ident.ToString(), new KeyValuePair<Thread, CancellationTokenSource>(router, canceller));
                router.Start();

            }
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
