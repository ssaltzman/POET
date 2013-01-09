Attribute VB_Name = "Module1"
Sub AddPOETChart()
'
' AddPOETChart Macro
'
    If ActiveSheet.ChartObjects.Count > 0 Then
        ActiveSheet.ChartObjects.Delete
    End If
    For Each s In ActiveWorkbook.Sheets
        ActiveSheet.Shapes.AddChart.Select
        ActiveChart.SetSourceData Source:=Sheets(s.Name).Range("B4:C10")
        ActiveChart.ChartType = xlColumnClustered
        ActiveChart.ChartTitle.Text = Sheets(s.Name).Range("A3")
        ActiveChart.Axes(xlValue).MinimumScale = 0
        ActiveChart.Axes(xlValue).MaximumScale = 7
        ActiveChart.Axes(xlValue).MajorUnit = 1
        ActiveChart.SeriesCollection(1).HasErrorBars = True
        
        ActiveChart.SeriesCollection(1).ErrorBar Direction:=xlY, Include:=xlBoth, _
        Type:=xlCustom, Amount:=Sheets(s.Name).Range("D5:D10"), MinusValues:=Sheets(s.Name).Range("D5:D10")
        Next s
End Sub
