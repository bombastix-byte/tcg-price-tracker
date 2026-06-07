import { useState, useCallback } from "react";
import {
  View,
  FlatList,
  StyleSheet,
  Text,
  ActivityIndicator,
  TouchableOpacity,
  Alert as RNAlert,
} from "react-native";
import { useFocusEffect } from "expo-router";
import { Ionicons } from "@expo/vector-icons";
import {
  getAlerts,
  deleteAlert,
  updateAlert,
  Alert,
} from "../../services/api";

// In production, get this from expo-notifications registration
const DEVICE_TOKEN = "ExponentPushToken[placeholder]";

export default function AlertsScreen() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);

  const loadAlerts = useCallback(async () => {
    setLoading(true);
    try {
      const data = await getAlerts(DEVICE_TOKEN);
      setAlerts(data);
    } catch {
      setAlerts([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useFocusEffect(
    useCallback(() => {
      loadAlerts();
    }, [loadAlerts])
  );

  const handleToggle = async (alert: Alert) => {
    try {
      await updateAlert(alert.id, { is_active: !alert.is_active });
      loadAlerts();
    } catch {
      RNAlert.alert("Error", "Failed to update alert");
    }
  };

  const handleDelete = (alert: Alert) => {
    RNAlert.alert("Delete Alert", "Are you sure?", [
      { text: "Cancel", style: "cancel" },
      {
        text: "Delete",
        style: "destructive",
        onPress: async () => {
          try {
            await deleteAlert(alert.id);
            loadAlerts();
          } catch {
            RNAlert.alert("Error", "Failed to delete alert");
          }
        },
      },
    ]);
  };

  const renderAlert = ({ item }: { item: Alert }) => (
    <View style={styles.alertCard}>
      <View style={{ flex: 1 }}>
        <Text style={styles.alertProduct}>Product #{item.product_id}</Text>
        <Text style={styles.alertDetail}>
          {item.direction === "below" ? "Below" : "Above"}{" "}
          {item.target_price.toFixed(2)} EUR
        </Text>
        <Text
          style={[
            styles.alertStatus,
            { color: item.is_active ? "#4ecca3" : "#666" },
          ]}
        >
          {item.is_active ? "Active" : "Inactive"}
        </Text>
      </View>
      <View style={styles.alertActions}>
        <TouchableOpacity onPress={() => handleToggle(item)}>
          <Ionicons
            name={item.is_active ? "pause-circle" : "play-circle"}
            size={28}
            color={item.is_active ? "#f0a500" : "#4ecca3"}
          />
        </TouchableOpacity>
        <TouchableOpacity onPress={() => handleDelete(item)}>
          <Ionicons name="trash" size={24} color="#e94560" />
        </TouchableOpacity>
      </View>
    </View>
  );

  return (
    <View style={styles.container}>
      {loading ? (
        <ActivityIndicator size="large" color="#e94560" style={{ marginTop: 40 }} />
      ) : (
        <FlatList
          data={alerts}
          keyExtractor={(item) => item.id.toString()}
          renderItem={renderAlert}
          contentContainerStyle={{ paddingBottom: 20 }}
          ListEmptyComponent={
            <Text style={styles.empty}>
              No price alerts set.{"\n"}Go to a product and set one!
            </Text>
          }
        />
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: "#16213e", padding: 16 },
  alertCard: {
    backgroundColor: "#1a1a2e",
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    flexDirection: "row",
    alignItems: "center",
    borderWidth: 1,
    borderColor: "#0f3460",
  },
  alertProduct: { color: "#e0e0e0", fontSize: 16, fontWeight: "600" },
  alertDetail: { color: "#8e8e93", fontSize: 14, marginTop: 4 },
  alertStatus: { fontSize: 12, marginTop: 4 },
  alertActions: { flexDirection: "row", gap: 16, alignItems: "center" },
  empty: {
    color: "#666",
    textAlign: "center",
    marginTop: 60,
    fontSize: 16,
    lineHeight: 24,
  },
});
