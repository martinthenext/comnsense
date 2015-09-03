﻿using System;
using System.Collections.Generic;
using System.Linq;
using System.Threading;
using Comnsense.ExcelAddin.Data;
using Microsoft.Office.Core;
using Microsoft.Office.Interop.Excel;
using ZeroMQ;

namespace Comnsense.ExcelAddin
{
    public partial class ThisAddIn
    {
        private ZContext _context;
        private ISerializer _serializer;
        private EventPublisher _publisher;
        private Dictionary<string, KeyValuePair<Thread, CancellationTokenSource>> _routers;
        private Dictionary<string, Cell[][]> _lastSelectedValues;

        private void ThisAddIn_Startup(object sender, EventArgs e)
        {
            _context = new ZContext();
            _serializer = new JsonNetSerializer();
            _publisher = new EventPublisher(_context, _serializer);
            _routers = new Dictionary<string, KeyValuePair<Thread, CancellationTokenSource>>();
            _lastSelectedValues = new Dictionary<string, Cell[][]>();

            Application.WorkbookOpen += ThisAddIn_WorkbookOpen;
            Application.WorkbookBeforeClose += ThisAddIn_WorkbookBeforeClose;
            Application.SheetSelectionChange += ThisAddIn_SheetSelectionChange;
            Application.SheetChange += ThisAddIn_SheetChange;
            Application.WorkbookBeforeClose += ThisAddIn_BeforeClose;
            ((AppEvents_Event) Application).NewWorkbook += ThisAddIn_NewWorkbook;
        }

        private void ThisAddIn_Shutdown(object sender, EventArgs e)
        {
            foreach (Thread thread in _routers.Select(pair => pair.Value.Key))
                thread.Join();
        }

        private void ThisAddIn_WorkbookOpen(Workbook wb)
        {
            string ident = GetWorkbookId(wb);
            RunRouter(wb, ident);
            _publisher.Send(Event.WorkbookOpen(ident, wb));
        }

        private void ThisAddIn_NewWorkbook(Workbook wb)
        {
            string ident = GetWorkbookId(wb);
            RunRouter(wb, ident);
            _publisher.Send(Event.WorkbookOpen(ident, wb));
        }

        private void ThisAddIn_WorkbookBeforeClose(Workbook wb, ref bool result)
        {
            string ident = GetWorkbookId(wb);
            _publisher.Send(Event.WorkbookBeforeClose(ident, wb));
        }

        private void ThisAddIn_BeforeClose(Workbook wb, ref bool result)
        {
            string ident = GetWorkbookId(wb);
            if (!_routers.ContainsKey(ident))
                return;
            KeyValuePair<Thread, CancellationTokenSource> pair;
            if (_routers.TryGetValue(ident, out pair))
                pair.Value.Cancel();
        }

        private void ThisAddIn_SheetSelectionChange(object sh, Range target)
        {
            Workbook wb = ((Worksheet) sh).Parent;
            string ident = GetWorkbookId(wb);
            if (_lastSelectedValues.ContainsKey(ident))
                _lastSelectedValues[ident] = Event.GetCellsFromRange(target);
            else
                _lastSelectedValues.Add(ident, Event.GetCellsFromRange(target));
        }

        private void ThisAddIn_SheetChange(object sh, Range target)
        {
            var worksheet = ((Worksheet) sh);
            Workbook wb = worksheet.Parent;
            string ident = GetWorkbookId(wb);
            if (_lastSelectedValues.ContainsKey(ident))
            {
                _publisher.Send(
                    Event.SheetChange(ident, worksheet, target, _lastSelectedValues[ident]));
            }
        }

        private string GetWorkbookId(Workbook workbook)
        {
            DocumentProperties properties = workbook.CustomDocumentProperties;
            var id = properties.GetStringPropertyValue("ComnsenseID");
            if (id != "")
                return id;

            id = Guid.NewGuid().ToString();
            properties.SetStringPropertyValue("ComnsenseID", id);
            return id;
        }

        private void RunRouter(Workbook workbook, string ident)
        {
            KeyValuePair<Thread, CancellationTokenSource> pair;
            if (_routers.TryGetValue(ident, out pair))
                if ((!pair.Key.IsAlive) || (pair.Value.IsCancellationRequested))
                    _routers.Remove(ident);

            if (_routers.ContainsKey(ident))
                return;

            var canceller = new CancellationTokenSource();
            var routerThread = new Thread(() =>
            {
                var router = new Router(_context, _serializer, workbook, ident);
                router.Run(canceller.Token);
            });
            _routers.Add(ident, new KeyValuePair<Thread, CancellationTokenSource>(routerThread, canceller));
            routerThread.Start();
        }

        private void InternalStartup()
        {
            Startup += ThisAddIn_Startup;
            Shutdown += ThisAddIn_Shutdown;
        }
    }
}