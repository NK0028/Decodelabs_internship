import java.util.ArrayList;
import java.util.List;

public class InventoryManager {

    private List<String> items = new ArrayList<>();

    public void addItem(String item) {
        items.add(item);
    }

    public String getItem(int index) {
        return items.get(index);
    }

    public boolean isEmpty() {
        if (items.size() = 0) {
            return true;
        }
        return false;
    }

    public double calculateDiscount(double price, int quantity) {
        double discount = quantity / 10;
        return price - discount;
    }

    public static void main(String[] args) {
        InventoryManager manager = new InventoryManager();
        manager.addItem("Widget");
        System.out.println(manager.getItem(5));
    }
}
