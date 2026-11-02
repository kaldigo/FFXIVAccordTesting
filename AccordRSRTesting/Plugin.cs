using Dalamud.Bindings.ImGui;
using Dalamud.Game.Command;
using Dalamud.Plugin;
using Dalamud.Plugin.Services;
using Newtonsoft.Json.Linq;
using System.Numerics;

namespace AccordRSRTesting;

public sealed class Plugin : IDalamudPlugin
{
    private readonly IDalamudPluginInterface pi;
    private readonly ICommandManager commands;
    private readonly IFramework framework;
    private bool open;
    private string? token;
    private long nextPoll;
    private string status = "Testing is off. Stable Accord settings are independent.";
    private JObject? discovery;
    private JObject? observation;

    public Plugin(IDalamudPluginInterface pluginInterface, ICommandManager commandManager, IFramework framework)
    {
        pi = pluginInterface;
        commands = commandManager;
        this.framework = framework;
        commands.AddHandler("/accordtest", new CommandInfo((_, _) => open = !open) {
            HelpMessage = "Open the opt-in RSR experiment. Separate from /accord." });
        pi.UiBuilder.Draw += Draw;
        pi.UiBuilder.OpenMainUi += Open;
        pi.UiBuilder.OpenConfigUi += Open;
        framework.Update += Update;
    }

    private void Open() => open = true;
    private JObject Call(string method) => Decode(pi.GetIpcSubscriber<string>("RotationSolverReborn.Accord" + method).InvokeFunc());
    private JObject Call(string method, string value) => Decode(pi.GetIpcSubscriber<string, string>("RotationSolverReborn.Accord" + method).InvokeFunc(value));
    private static JObject Decode(string json)
    {
        var result = JObject.Parse(json);
        if (result.Value<bool>("Success") != true) throw new InvalidOperationException(result.Value<string>("Error") ?? "Engine request rejected.");
        return result;
    }
    private void CheckEngine()
    {
        if (!pi.InstalledPlugins.Any(p => p.InternalName == "AccordRSREngine" && p.IsLoaded))
            throw new InvalidOperationException("Load Rotation Solver Reborn - Accord Test first.");
        discovery = Call("Discover");
        if (discovery.Value<string>("Identity") != "AccordRSREngine" || discovery.Value<int>("ApiVersion") != 1)
            throw new InvalidOperationException("The experimental engine does not match this client.");
    }
    private void Try(Action action)
    {
        try { action(); }
        catch (Exception ex) { status = ex.Message; token = null; observation = null; }
    }
    private void Begin()
    {
        CheckEngine();
        token = Call("BeginSession").Value<string>("Token") ?? throw new InvalidOperationException("Engine returned no session.");
        status = "Test session enabled. Use Start rotation when ready; RSR settings control its behaviour.";
    }
    private void End()
    {
        var old = token;
        token = null;
        if (old != null) Call("EndSession", old);
        observation = null;
        status = "Testing is off.";
    }
    private void Update(IFramework _)
    {
        if (Environment.TickCount64 < nextPoll) return;
        nextPoll = Environment.TickCount64 + 1000;
        if (token == null && !open) return;
        Try(() => {
            CheckEngine();
            if (token != null) Call("Heartbeat", token);
            observation = Call("Observe");
        });
    }
    private void Draw()
    {
        if (!open) return;
        ImGui.SetNextWindowSize(new Vector2(710, 530), ImGuiCond.FirstUseEver);
        if (ImGui.Begin("Accord RSR Test###AccordRSRTesting", ref open))
        {
            ImGui.TextWrapped("RSR-based Accord redesign: native rotation baseline and selector workbench.");
            ImGui.TextWrapped("This build does not apply hotbars or import stable Accord choices. The old four automation switches are deliberately not carried over.");
            ImGui.Separator();
            ImGui.TextWrapped(status);
            ImGui.TextWrapped("Before testing, disable stable Accord, Wrath and stock RSR. Each client load starts with testing off. Losing the client heartbeat stops the test engine.");
            if (token == null)
            {
                if (ImGui.Button("Enable test session")) Try(Begin);
            }
            else
            {
                if (ImGui.Button("End test session")) Try(End);
                if (ImGui.Button("Start rotation with manual enemy targeting")) Try(() => { Call("Run", token!); status = "RSR rotation started. Manual targeting still automatically executes actions."; });
                ImGui.SameLine();
                if (ImGui.Button("Stop rotation")) Try(() => { Call("Stop", token!); status = "Rotation stopped; test session remains enabled."; });
            }
            ImGui.TextWrapped("Configure job rotation and automatic healing/defence in the test engine's own settings. Existing RSR settings apply; these are not yet Accord intent policies.");
            ImGui.Separator();
            if (discovery != null) ImGui.TextUnformatted("Engine " + discovery.Value<string>("EngineVersion") + " | " + discovery.Value<string>("Stage"));
            if (observation != null)
            {
                ImGui.TextUnformatted($"Job: {observation["Job"]} | Rotation running: {observation["Running"]} | Next action ID: {observation["NextAction"]}");
                ImGui.TextWrapped("These are cached suggestions, not executable intent buttons. Open the test engine's full control window to populate them. A blank result means no suggestion is available.");
                if (observation["Selectors"] is JObject selectors)
                    foreach (var property in selectors.Properties())
                        ImGui.TextUnformatted($"{System.Text.RegularExpressions.Regex.Replace(property.Name, "([a-z])([A-Z])", "$1 $2")}: {property.Value}");
                else ImGui.TextWrapped("No selector preview available.");
            }
        }
        ImGui.End();
    }
    public void Dispose()
    {
        try { End(); } catch { /* The session lease also expires if the engine is already gone. */ }
        framework.Update -= Update;
        pi.UiBuilder.Draw -= Draw;
        pi.UiBuilder.OpenMainUi -= Open;
        pi.UiBuilder.OpenConfigUi -= Open;
        commands.RemoveHandler("/accordtest");
    }
}
