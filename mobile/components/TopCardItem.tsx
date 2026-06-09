import { View, Text, Image, StyleSheet } from "react-native";
import { TopCard } from "../services/api";

interface Props {
  card: TopCard;
  rank: number;
}

export default function TopCardItem({ card, rank }: Props) {
  return (
    <View style={styles.container}>
      {card.image_url ? (
        <Image source={{ uri: card.image_url }} style={styles.image} resizeMode="contain" />
      ) : (
        <View style={[styles.image, styles.placeholder]} />
      )}
      <View style={styles.info}>
        <Text style={styles.rank}>#{rank}</Text>
        <Text style={styles.name} numberOfLines={2}>
          {card.name}
        </Text>
      </View>
      <Text style={styles.price}>
        {card.price_eur != null ? `${card.price_eur.toFixed(2)} EUR` : "N/A"}
      </Text>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    width: 130,
    backgroundColor: "#1a1a2e",
    borderRadius: 10,
    padding: 8,
    alignItems: "center",
    borderWidth: 1,
    borderColor: "#0f3460",
    marginRight: 10,
  },
  image: {
    width: 100,
    height: 140,
    borderRadius: 6,
  },
  placeholder: {
    backgroundColor: "#0f3460",
  },
  info: {
    alignItems: "center",
    marginTop: 6,
  },
  rank: {
    color: "#e94560",
    fontSize: 12,
    fontWeight: "700",
  },
  name: {
    color: "#e0e0e0",
    fontSize: 12,
    fontWeight: "600",
    textAlign: "center",
    marginTop: 2,
    height: 32,
  },
  price: {
    color: "#4ecca3",
    fontSize: 14,
    fontWeight: "700",
    marginTop: 4,
  },
});
